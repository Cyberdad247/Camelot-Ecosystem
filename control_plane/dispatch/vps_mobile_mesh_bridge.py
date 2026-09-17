# SPDX-License-Identifier: MIT
import hmac
import json, os, logging
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Optional

from control_plane.dispatch.vps_hermes_links import attach_vps_hermes_links
from control_plane.infra.mesh_topology import (
    ABSENT_MESH_NODES,
    HUB_NODE_ID,
    HUB_PUBLIC_IP,
    HUB_TAILSCALE_IP,
    MESH_NODES,
    ip_of,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s')
LOG = logging.getLogger('VpsMobileMeshBridge')

VPS_HOST = '162.35.107.134'
# Every address below derives from control_plane.infra.mesh_topology — the single
# source reconciled against live `tailscale status`. Do not reintroduce literals
# here. This file previously carried its own copy, which is how `kba_services`
# (absent from the tailnet entirely) came to be published as a live node, and how
# the hub came to advertise the kba_services address as its own.
VPS_TAILSCALE_IP = HUB_TAILSCALE_IP
LOCAL_CYBERTRONIA_IP = ip_of('cybertronia')
FATHERS_CAMELOT_TAILSCALE = ip_of('fothers_camelot')
MOBILE_TAILSCALE_IP = ip_of('vashawns_s26_ultra')
MOTO_TAILSCALE_IP = ip_of('motorola_moto_g_power')
LOCAL_BIFROST_PORT = int(os.getenv('BIFROST_PORT', 3001))
BRIDGE_PORT = int(os.getenv('VPS_BRIDGE_PORT', 8095))

TOPOLOGY_PATH = os.path.join(os.path.dirname(__file__), '../../03_VAULT/runtime_state/sovereign_mesh_topology.json')

# The id this bridge serves the hub under. `attach_vps_hermes_links` keys the
# inference links on this historical name, so it survives even though the
# canonical node id is HUB_NODE_ID.
SERVED_HUB_ID = 'vps_hub_kvm563'

# Canonical id -> served id, where the two differ.
_SERVED_ID_ALIASES = {HUB_NODE_ID: SERVED_HUB_ID}

# Keys the state file may never supply. `mesh_topology` owns addressing, so a
# stale or hand-edited state file cannot redirect traffic at another host.
_ADDRESS_KEYS = frozenset({'tailscale_ip', 'ip', 'public_ip'})

# --- Hermes Prime liveness ---------------------------------------------------
#
# `camelot-hermes-prime.timer` drives one MGV cycle every 60s on the hub (see
# infra/systemd/camelot-hermes-prime.timer). HERMES_PRIME status is therefore
# DERIVED from how recently the engine actually wrote a cycle, never asserted.
#
# This endpoint previously hardcoded "ALWAYS_ON_HUB". At the time it served that
# string, camelot-hermes-prime.service was disabled, had never been enabled, and
# had zero journal entries -- and its ExecStart (`--loop 60`) could not run at
# all. The endpoint was reporting a status it had no evidence for, and no test
# could catch the lie because the string was a constant.
#
# A cycle is treated as current for GRACE x cadence before the status degrades,
# so one slow or skipped run does not flap the dashboard.
HERMES_PRIME_CADENCE_S = 60
HERMES_PRIME_GRACE_MULTIPLIER = 3

PHIAL_STATE_PATH = os.path.join(
    os.path.dirname(__file__), '../../03_VAULT/runtime_state/hermes_prime_phial.json'
)


def read_phial_state() -> dict[str, Any]:
    """PhialEngine state as last written, or {} if absent or unreadable."""
    if not os.path.exists(PHIAL_STATE_PATH):
        return {}
    try:
        with open(PHIAL_STATE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        LOG.warning(f"phial state unreadable: {e}")
        return {}


def _parse_ts(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        ts = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
    except ValueError:
        return None
    return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)


def _latest_cycle(state: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Most recent memory entry carrying a parseable timestamp."""
    memory = state.get('memory') if isinstance(state, dict) else None
    if not isinstance(memory, list):
        return None
    for entry in reversed(memory):
        if isinstance(entry, dict) and _parse_ts(entry.get('ts')) is not None:
            return entry
    return None


def hermes_prime_status(
    state: Optional[dict[str, Any]] = None,
    now: Optional[datetime] = None,
) -> dict[str, Any]:
    """Derive HERMES_PRIME liveness from the state the engine actually writes.

    Returns ALWAYS_ON_HUB only when a cycle landed inside the freshness window.
    Otherwise STALE (state present but old), UNPARSEABLE (state present, no
    usable timestamp) or NO_STATE (nothing written yet). Diagnostics ride along
    so a dashboard can show why, rather than just a degraded label.
    """
    if state is None:
        state = read_phial_state()
    if not isinstance(state, dict):
        state = {}
    if now is None:
        now = datetime.now(timezone.utc)

    memory = state.get('memory')
    result: dict[str, Any] = {
        "status": "NO_STATE",
        "cycles": len(memory) if isinstance(memory, list) else 0,
        "last_cycle_ts": None,
        "last_cycle_age_s": None,
        "fresh_within_s": HERMES_PRIME_CADENCE_S * HERMES_PRIME_GRACE_MULTIPLIER,
        "cadence_s": HERMES_PRIME_CADENCE_S,
    }

    latest = _latest_cycle(state)
    if latest is None:
        if result["cycles"]:
            result["status"] = "UNPARSEABLE"
        return result

    ts = _parse_ts(latest.get('ts'))
    if ts is None:  # pragma: no cover - _latest_cycle already guarantees a ts
        result["status"] = "UNPARSEABLE"
        return result

    age = (now - ts).total_seconds()
    result["last_cycle_ts"] = latest.get('ts')
    result["last_cycle_age_s"] = round(age, 3)
    result["status"] = "ALWAYS_ON_HUB" if age <= result["fresh_within_s"] else "STALE"
    return result


def _authoritative_nodes() -> dict[str, dict[str, Any]]:
    """The node set the single source declares — the non-negotiable part.

    Addresses are written only from here. The state file may later enrich these
    entries with observed metadata, but it can never name a node this function
    does not declare, and can never move one.
    """
    nodes: dict[str, dict[str, Any]] = {}
    for n in MESH_NODES:
        nodes[_SERVED_ID_ALIASES.get(n.id, n.id)] = {
            "tailscale_ip": n.ip,
            "role": n.role,
        }
    nodes[SERVED_HUB_ID].update({
        "public_ip": HUB_PUBLIC_IP,
        "hostname": "vps-camelot-hub",
        "governing_knights": ["HERMES_PRIME", "SIR_HEIMDALL"],
        "always_on": True,
    })
    return nodes


def _read_topology_state() -> Optional[dict[str, Any]]:
    """Best-effort read of the on-disk state file. Never fatal, never binding."""
    if not os.path.exists(TOPOLOGY_PATH):
        return None
    try:
        with open(TOPOLOGY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        LOG.warning(f"Failed to read topology file: {e}")
        return None


def load_mesh_topology() -> dict:
    """Serve the mesh topology, sourced from `control_plane.infra.mesh_topology`.

    The single source is authoritative for *which nodes exist and at what
    address*. The state file on disk records observed metadata (os, version,
    designation, ports) and used to override the node set wholesale — returning
    it verbatim on the first line. That is how two nodes absent from the tailnet
    kept being served as live long after every Python inventory had been
    corrected: a stale file resurrected them on every read, and the projection
    written as the fix was never reached.

    The file can now only *enrich* nodes the source already declares. Anything it
    names that the source does not know is dropped, and said so in the log.
    """
    nodes = _authoritative_nodes()
    state = _read_topology_state()

    if state:
        declared = state.get("nodes") or {}
        suppressed = sorted(k for k in declared if k not in nodes)
        if suppressed:
            LOG.warning(
                "topology state file declares node(s) absent from mesh_topology; "
                "suppressed: %s",
                ", ".join(suppressed),
            )
        for node_id, meta in declared.items():
            node = nodes.get(node_id)
            if node is None or not isinstance(meta, dict):
                continue  # not in the source => phantom, dropped above
            for key, value in meta.items():
                if key in _ADDRESS_KEYS:
                    continue  # the source owns addressing, unconditionally
                node[key] = value

    topology: dict[str, Any] = {
        "system": (state or {}).get("system", "CAMELOT-OS Sovereign Autonomous Ecosystem"),
        "version": (state or {}).get("version", "vMAX Singularity"),
        "tailscale_account": (state or {}).get("tailscale_account", "Cyberdad247@github"),
        "timestamp": (state or {}).get("timestamp"),
        "nodes": nodes,
        # Never published as reachable — carried so a consumer can explain an
        # absence instead of reporting a node offline forever.
        "absent_nodes": {
            n.id: {"tailscale_ip": n.ip, "role": n.role, "status": n.status}
            for n in ABSENT_MESH_NODES
        },
    }
    return attach_vps_hermes_links(topology)

def is_mesh_request_authorized(headers: dict) -> bool:
    """Require the runtime-only mesh token for topology and telemetry reads."""
    expected = os.getenv("MESH_BRIDGE_TOKEN", "")
    provided = headers.get("x-camelot-token", "")
    if not expected or not provided:
        return False
    return hmac.compare_digest(provided, expected)


class MeshBridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not is_mesh_request_authorized(self.headers):
            self._send_json({"error": "mesh bridge authentication failed"}, code=401)
            return
        if self.path in ['/mesh/status', '/', '/api/topology']:
            topology_data = load_mesh_topology()
            status = {
                'mesh_status': 'ONLINE',
                'timestamp': topology_data.get('timestamp'),
                'account': topology_data.get('tailscale_account', 'Cyberdad247@github'),
                'nodes': topology_data.get('nodes', {}),
                'bifrost_co_governors': ['HERMES_PRIME', "SIR_HEIMDALL"],
            }
            self._send_json(status)
        elif self.path in ['/bifrost/knights', '/api/bifrost/knights']:
            hermes = hermes_prime_status()
            knights = [
                {"id": "SIR_HEIMDALL", "role": "Bifrost Guardian & Boundary Sentinel", "status": "ALWAYS_ON_HUB"},
                {
                    "id": "HERMES_PRIME",
                    "role": "Always-on VPS Co-Pilot & MGV Synthesis",
                    "status": hermes["status"],
                    "last_cycle_age_s": hermes["last_cycle_age_s"],
                    "cycles": hermes["cycles"],
                },
                {"id": "SIR_LANCELOT", "role": "Kinetic Edge & Frontline Defense", "status": "ACTIVE_ESCORT"},
                {"id": "SIR_GALAHAD", "role": "Verification, Chivalric Purity & Z3 Formal Gate", "status": "ACTIVE_ESCORT"},
                {"id": "SIR_SENTINEL", "role": "AgentArmor, Zero-Trust Leases & Security Shield", "status": "ACTIVE_ESCORT"},
                {"id": "LADY_MNEMOSYNE", "role": "Living Memory Guardian & World Tree Spine", "status": "ACTIVE_ESCORT"},
                {"id": "SIR_HELIO", "role": "Voice OS & Phonetic Mesh Dispatch", "status": "ACTIVE_ESCORT"},
            ]
            self._send_json({"bifrost_knights": knights, "hub": "162.35.107.134"})
        elif self.path in ['/hermes/telemetry', '/api/hermes']:
            hermes = hermes_prime_status()
            self._send_json({
                "agent": "HERMES_PRIME",
                "role": "VPS Hub Co-Pilot & Research Synthesis",
                "host": VPS_HOST,
                "status": hermes["status"],
                "last_cycle_age_s": hermes["last_cycle_age_s"],
                "phial_engine": read_phial_state(),
            })
        elif self.path in ['/telemetry/cockpit', '/api/cockpit', '/excalibur/cockpit']:
            always_on_path = os.path.join(os.path.dirname(__file__), '../../03_VAULT/runtime_state/cybertronia_always_on.json')
            cockpit_state = {}
            if os.path.exists(always_on_path):
                try:
                    with open(always_on_path, 'r', encoding='utf-8') as f:
                        cockpit_state = json.load(f)
                except Exception:
                    pass
            self._send_json({
                "source": "cybertronia_always_on",
                "mobile_sentinel": MOBILE_TAILSCALE_IP,
                "cockpit": "Excalibur Command Center (S26 Ultra)",
                "live_state": cockpit_state or {"status": "ACTIVE_SENTINEL", "host": "cybertronia"},
            })
        elif self.path in ['/telemetry/moto', '/api/moto', '/moto/sentinel', '/api/sentinel/moto']:
            self._send_json({
                "source": "motorola_moto_g_power",
                "tailscale_ip": MOTO_TAILSCALE_IP,
                "designation": "AUXILIARY_MOBILE_SENTINEL",
                "role": "Auxiliary Mobile Sentinel & Backup Telemetry Relay",
                "model": "Motorola Moto G Power 5G (2024)",
                "status": "ONLINE_STANDBY",
                "active_ports": {"aux_sentinel_relay": 8092, "termux_ssh": 8023},
                "primary_cockpit_peer": MOBILE_TAILSCALE_IP,
                "mesh_gateway": f"http://{LOCAL_CYBERTRONIA_IP}:{BRIDGE_PORT}",
                "bifrost_port": LOCAL_BIFROST_PORT,
                "governing_knight": "SIR_HEIMDALL",
            })
        elif self.path in ['/mesh/nodes', '/api/mesh/nodes']:
            topology_data = load_mesh_topology()
            self._send_json({
                "account": topology_data.get('tailscale_account', 'Cyberdad247@github'),
                "nodes": topology_data.get('nodes', {}),
            })
        elif self.path in ['/heimdall/governance', '/api/heimdall']:
            gov_path = os.path.join(os.path.dirname(__file__), '../../03_VAULT/runtime_state/heimdall_bifrost_governance_latest.json')
            gov_data = {}
            if os.path.exists(gov_path):
                try:
                    with open(gov_path, 'r', encoding='utf-8') as f:
                        gov_data = json.load(f)
                except Exception:
                    pass
            self._send_json(gov_data or {"status": "GOVERNING", "owner": "sir_heimdall"})
        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, data: dict, code: int = 200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

def run_server():
    server = HTTPServer(('0.0.0.0', BRIDGE_PORT), MeshBridgeHandler)
    LOG.info(f'Full Mesh Bridge active on port {BRIDGE_PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == '__main__':
    run_server()
