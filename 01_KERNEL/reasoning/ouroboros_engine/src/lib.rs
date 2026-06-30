pub mod prefetcher;
pub mod quantizer;
pub mod mamba;
pub mod trellis;

#[cfg(feature = "pyo3")]
use pyo3::prelude::*;

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
#[pymodule]
fn ouroboros_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(log_execution, m)?)?;
    m.add_function(wrap_pyfunction!(get_history, m)?)?;
    m.add_function(wrap_pyfunction!(get_stats, m)?)?;
    m.add_function(wrap_pyfunction!(export_all, m)?)?;
    m.add_function(wrap_pyfunction!(trigger_pending_compression, m)?)?;
    Ok(())
}