pub mod prefetcher;
pub mod quantizer;
pub mod mamba;
pub mod trellis;

#[cfg(feature = "pyo3")]
use pyo3::prelude::*;
#[cfg(feature = "pyo3")]
use pyo3::types::PyList;
#[cfg(feature = "pyo3")]
use std::sync::OnceLock;
#[cfg(feature = "pyo3")]
use contracts::{
    CartridgeSwitchAckV1, CartridgeSwitchRequestV1, TriageRequestV1, TriageScoreWireV1,
    pack as msgpack_pack, unpack as msgpack_unpack,
};

// Singleton holder — CartridgeManager carries working state across
// Scabbard-Protocol switches, so a single instance per process is required.
// AnyaGate is intentionally NOT singletonized: its `__init__` is empty and
// re-instantiation is cheap. (SoulRouter() runs once per call regardless of
// AnyaGate instance, so AnyaGate-singletonization saves nothing.)
#[cfg(feature = "pyo3")]
static CARTRIDGE_SINGLETON: OnceLock<Py<PyAny>> = OnceLock::new();

#[cfg(feature = "pyo3")]
pub mod ledger;

#[cfg(feature = "pyo3")]
#[pyfunction]
#[pyo3(signature = (directive, intent=None, domain=None, complexity=0, knight=String::new(), status=String::new(), result=None, duration_ms=0, files_created=None))]
#[allow(clippy::too_many_arguments)]
fn log_execution(
    directive: String,
    intent: Option<String>,
    domain: Option<String>,
    complexity: i64,
    knight: String,
    status: String,
    result: Option<String>,
    duration_ms: i64,
    files_created: Option<String>,
) -> PyResult<()> {
    ledger::append(directive, intent, domain, complexity, knight, status, result, duration_ms, files_created)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
}

#[cfg(feature = "pyo3")]
#[pyfunction]
#[pyo3(signature = (limit=20))]
fn get_history(py: Python<'_>, limit: usize) -> PyResult<PyObject> {
    let entries = ledger::get_history(Some(limit))
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    
    let py_list = pyo3::types::PyList::empty(py);
    for entry in entries {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("id", entry.id)?;
        dict.set_item("timestamp", entry.timestamp)?;
        dict.set_item("directive", entry.directive)?;
        dict.set_item("intent", entry.intent)?;
        dict.set_item("domain", entry.domain)?;
        dict.set_item("complexity", entry.complexity)?;
        dict.set_item("knight", entry.knight)?;
        dict.set_item("status", entry.status)?;
        dict.set_item("result", entry.result)?;
        dict.set_item("duration_ms", entry.duration_ms)?;
        dict.set_item("files_created", entry.files_created)?;
        py_list.append(dict)?;
    }
    
    Ok(py_list.into())
}

#[cfg(feature = "pyo3")]
#[pyfunction]
fn get_stats(py: Python<'_>) -> PyResult<PyObject> {
    let stats = ledger::get_stats()
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    
    let py_list = pyo3::types::PyList::empty(py);
    for stat in stats {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("knight", stat.knight)?;
        dict.set_item("total_runs", stat.total_runs)?;
        dict.set_item("successes", stat.successes)?;
        dict.set_item("failures", stat.failures)?;
        dict.set_item("blocked", stat.blocked)?;
        dict.set_item("avg_duration_ms", stat.avg_duration_ms)?;
        py_list.append(dict)?;
    }
    
    Ok(py_list.into())
}

#[cfg(feature = "pyo3")]
#[pyfunction]
fn export_all(py: Python<'_>) -> PyResult<PyObject> {
    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("history", get_history(py, 9999)?)?;
    dict.set_item("stats", get_stats(py)?)?;
    Ok(dict.into())
}

#[cfg(feature = "pyo3")]
#[pyfunction]
fn trigger_pending_compression() -> PyResult<u64> {
    ledger::flush_pending().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
}

#[cfg(feature = "pyo3")]
#[pyfunction]
fn clear_ledger() -> PyResult<()> {
    ledger::clear().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
}

// ── WASM actor -> control_plane bridge (reuse-before-reimplement scope PR) ──
//
// Imports the existing AnyaGate.triage / CartridgeManager.switch instead of
// duplicating triage or cartridge logic. Contracts crate handles the
// msgpack wire boundary so this stays a thin adapter.

#[cfg(feature = "pyo3")]
fn ensure_repo_root_on_path(py: Python<'_>) -> PyResult<()> {
    use std::path::Path;
    // CARGO_MANIFEST_DIR == 01_KERNEL/reasoning/ouroboros_engine → up 3 to repo root.
    let manifest = env!("CARGO_MANIFEST_DIR");
    let root = Path::new(manifest)
        .join("..")
        .join("..")
        .join("..")
        .canonicalize()
        .unwrap_or_else(|_| Path::new(manifest).join("..").join("..").join(".."))
        .to_string_lossy()
        .into_owned();
    let sys = py.import("sys")?;
    // downcast_into CONSUMES the Bound<PyAny> returned by getattr, returning
    // an owned Bound<PyList>. The earlier `.downcast()` (borrowing) triggered
    // E0716 "temporary dropped while borrowed" because getattr's return is a
    // statement-bound temporary that the borrow out-lives.
    let path: Bound<'_, PyList> = sys.getattr("path")?.downcast_into()?;
    // Idempotent: don't pollute sys.path with duplicates.
    let already: bool = path
        .call_method1("__contains__", (root.as_str(),))?
        .extract()?;
    if !already {
        path.insert(0, root.as_str())?;
    }
    Ok(())
}

#[cfg(feature = "pyo3")]
fn get_cartridge_manager(py: Python<'_>) -> PyResult<Py<PyAny>> {
    if let Some(m) = CARTRIDGE_SINGLETON.get() {
        // Cache hit: `Py::clone_ref(&self, py)` takes `&Py<T>` and returns
        // owned `Py<T>` with a refcount bump. Working_context state in the
        // underlying CartridgeManager survives across calls.
        return Ok(m.clone_ref(py));
    }
    ensure_repo_root_on_path(py)?;
    let module = py.import("control_plane.cartridge_manager")?;
    let class_obj: Bound<'_, PyAny> = module.getattr("CartridgeManager")?;
    let instance: Bound<'_, PyAny> = class_obj.call0()?;
    // `Bound::unbind(self) -> Py<T>` consumes the Bound and returns the
    // owned unbound Py handle. pyo3 0.21+ canonical API (safer than
    // `.into()` whose target type can be ambiguous when the borrow chain
    // blurs ownership).
    let rc: Py<PyAny> = instance.unbind();
    let _ = CARTRIDGE_SINGLETON.set(rc.clone_ref(py));
    Ok(rc)
}

#[cfg(feature = "pyo3")]
fn get_anya_gate(py: Python<'_>) -> PyResult<Py<PyAny>> {
    ensure_repo_root_on_path(py)?;
    let module = py.import("control_plane.anya_gate")?;
    let class_obj: Bound<'_, PyAny> = module.getattr("AnyaGate")?;
    let instance: Bound<'_, PyAny> = class_obj.call0()?;
    Ok(instance.unbind())
}

#[cfg(feature = "pyo3")]
#[pyfunction]
/// Wire entry-point: pack a `CartridgeSwitchRequestV1` and unpack a
/// `CartridgeSwitchAckV1`. Reuses the existing `CartridgeManager.switch`
/// (Scabbard Protocol) on the Python side — does NOT reimplement the swap.
fn switch_cartridge_v1(py: Python<'_>, bytes: Vec<u8>) -> PyResult<Vec<u8>> {
    let req: CartridgeSwitchRequestV1 = msgpack_unpack(&bytes)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("unpack switch req: {e}")))?;
    let cm = get_cartridge_manager(py)?;
    let result = cm.bind(py).call_method1("switch", (req.name.as_str(),))?;
    let name: String = result.getattr("name")?.extract()?;
    let title: String = result.getattr("title")?.extract()?;
    let lead: String = result.getattr("lead_knight")?.extract()?;
    let activated_at: f64 = result.getattr("activated_at")?.extract()?;
    let ack = CartridgeSwitchAckV1 { name, title, lead_knight: lead, activated_at };
    msgpack_pack(&ack).map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("pack switch ack: {e}")))
}

#[cfg(feature = "pyo3")]
#[pyfunction]
/// Wire entry-point: pack a `TriageRequestV1` and unpack a
/// `TriageScoreWireV1`. Reuses the existing `AnyaGate.triage` on the Python
/// side — does NOT reimplement triage (risk_entropy, HITL tier, shatterpoints).
fn triage_intent_v1(py: Python<'_>, bytes: Vec<u8>) -> PyResult<Vec<u8>> {
    let req: TriageRequestV1 = msgpack_unpack(&bytes)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("unpack triage req: {e}")))?;
    let gate = get_anya_gate(py)?;
    let score = gate.bind(py).call_method1("triage", (req.intent.as_str(),))?;
    let hitl: String = score.getattr("hitl_tier")?.extract()?;
    let entropy: f32 = score.getattr("risk_entropy")?.extract()?;
    let cartridge: String = score.getattr("cartridge_hint")?.extract()?;
    let knight: String = score.getattr("assigned_knight")?.extract()?;
    let needs = hitl == "HUMAN_GATE";
    let wire = TriageScoreWireV1 {
        hitl_tier: hitl,
        risk_entropy: entropy,
        cartridge_hint: cartridge,
        assigned_knight: knight,
        needs_human: needs,
    };
    msgpack_pack(&wire).map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("pack score wire: {e}")))
}

#[cfg(feature = "pyo3")]
#[pymodule]
fn ouroboros_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(log_execution, m)?)?;
    m.add_function(wrap_pyfunction!(get_history, m)?)?;
    m.add_function(wrap_pyfunction!(get_stats, m)?)?;
    m.add_function(wrap_pyfunction!(export_all, m)?)?;
    m.add_function(wrap_pyfunction!(trigger_pending_compression, m)?)?;
    m.add_function(wrap_pyfunction!(clear_ledger, m)?)?;
    m.add_function(wrap_pyfunction!(triage_intent_v1, m)?)?;
    m.add_function(wrap_pyfunction!(switch_cartridge_v1, m)?)?;
    Ok(())
}