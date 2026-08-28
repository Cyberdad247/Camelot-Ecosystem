# SPDX-License-Identifier: MIT
import json, os, logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s')
LOG = logging.getLogger('VpsMobileMeshBridge')

VPS_HOST = '162.35.107.134'
VPS_TAILSCALE_IP = '100.110.180.18'
VPS_KBA_TAILSCALE = '100.71.218.75'
FATHERS_CAMELOT_TAILSCALE = '100.121.48.50'
MOBILE_TAILSCALE_IP = '100.106.246.126'
LOCAL_CYBERTRONIA_IP = '100.118.224.52'
LOCAL_BIFROST_PORT = int(os.getenv('BIFROST_PORT', 3001))
BRIDGE_PORT = int(os.getenv('VPS_BRIDGE_PORT', 8095))

TOPOLOGY_PATH = os.path.join(os.path.dirname(__file__), '../../03_VAULT/runtime_state/sovereign_mesh_topology.json')

def load_mesh_topology() -> dict:
    if os.path.exists(TOPOLOGY_PATH):
        try:
            with open(TOPOLOGY_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            LOG.warning(f"Failed to read topology file: {e}")
    return {
        "system": "CAMELOT-OS Sovereign Autonomous Ecosystem",
        "nodes": {
            "cybertronia": {"tailscale_ip": LOCAL_CYBERTRONIA_IP, "role": "Primary Kinetic Execution Node"},
            "vashawns_s26_ultra": {"tailscale_ip": MOBILE_TAILSCALE_IP, "role": "Excalibur Command Center"},
            "fothers_camelot": {"tailscale_ip": FATHERS_CAMELOT_TAILSCALE, "role": "Secondary Windows Node"},
            "lakesha": {"tailscale_ip": "100.100.155.55", "role": "Lakisha Voice OS Host"},
            "camelot_relay_modal": {"tailscale_ip": "100.84.98.39", "role": "Cloud Relay & Modal Bridge"},
            "kba_services": {"tailscale_ip": VPS_KBA_TAILSCALE, "role": "KBA Remote Services"},
            "motorola_moto_g_power": {"tailscale_ip": "100.89.129.105", "role": "Auxiliary Mobile Sentinel"},
            "vps_hub_kvm563": {
                "public_ip": VPS_HOST,
                "tailscale_ip": VPS_KBA_TAILSCALE,
                "role": "Camelot-OS Sovereign Hub & Control Plane",
                "governing_knights": ["HERMES_PRIME", "SIR_HEIMDALL"],
                "always_on": True,
            }
        }
    }

class MeshBridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
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
            knights = [
                {"id": "SIR_HEIMDALL", "role": "Bifrost Guardian & Boundary Sentinel", "status": "ALWAYS_ON_HUB"},
                {"id": "HERMES_PRIME", "role": "Always-on VPS Co-Pilot & MGV Synthesis", "status": "ALWAYS_ON_HUB"},
                {"id": "SIR_LANCELOT", "role": "Kinetic Edge & Frontline Defense", "status": "ACTIVE_ESCORT"},
                {"id": "SIR_GALAHAD", "role": "Verification, Chivalric Purity & Z3 Formal Gate", "status": "ACTIVE_ESCORT"},
                {"id": "SIR_SENTINEL", "role": "AgentArmor, Zero-Trust Leases & Security Shield", "status": "ACTIVE_ESCORT"},
                {"id": "LADY_MNEMOSYNE", "role": "Living Memory Guardian & World Tree Spine", "status": "ACTIVE_ESCORT"},
                {"id": "SIR_HELIO", "role": "Voice OS & Phonetic Mesh Dispatch", "status": "ACTIVE_ESCORT"},
            ]
            self._send_json({"bifrost_knights": knights, "hub": "162.35.107.134"})
        elif self.path in ['/hermes/telemetry', '/api/hermes']:
            phial_state_path = os.path.join(os.path.dirname(__file__), '../../03_VAULT/runtime_state/hermes_prime_phial.json')
            phial_data = {}
            if os.path.exists(phial_state_path):
                try:
                    with open(phial_state_path, 'r', encoding='utf-8') as f:
                        phial_data = json.load(f)
                except Exception:
                    pass
            self._send_json({
                "agent": "HERMES_PRIME",
                "role": "VPS Hub Co-Pilot & Research Synthesis",
                "host": VPS_HOST,
                "phial_engine": phial_data,
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
