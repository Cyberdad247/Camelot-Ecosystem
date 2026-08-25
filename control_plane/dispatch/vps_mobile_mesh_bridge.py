# SPDX-License-Identifier: MIT
import sys, json, os, urllib.request, logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s')
LOG = logging.getLogger('VpsMobileMeshBridge')

VPS_HOST = '162.35.107.134'
VPS_KBA_TAILSCALE = '100.71.218.75'
FATHERS_CAMELOT_TAILSCALE = '100.121.48.50'
MOBILE_TAILSCALE_IP = '100.106.246.126'
LOCAL_CYBERTRONIA_IP = '100.118.224.52'
LOCAL_BIFROST_PORT = int(os.getenv('BIFROST_PORT', 3001))
BRIDGE_PORT = int(os.getenv('VPS_BRIDGE_PORT', 8095))

class MeshBridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/mesh/status', '/']:
            status = {
                'mesh_status': 'ONLINE',
                'topology': {
                    'vps_control_plane': {
                        'host_server': 'KVM563',
                        'vm_id': 'vps3573819',
                        'public_ip': VPS_HOST,
                        'agent': 'HERMES_PRIME'
                    },
                    'kba_services_node': {
                        'tailscale_ip': VPS_KBA_TAILSCALE,
                        'role': 'Kickbox Audio & WebRTC Remote Services'
                    },
                    'fathers_camelot_node': {
                        'tailscale_ip': FATHERS_CAMELOT_TAILSCALE,
                        'role': 'Sovereign Windows Secondary & Failover Rig'
                    },
                    'mobile_sentinel': {
                        'tailscale_ip': MOBILE_TAILSCALE_IP,
                        'role': 'Excalibur Command Center (S26 Ultra)'
                    },
                    'cybertronia_host': {
                        'tailscale_ip': LOCAL_CYBERTRONIA_IP,
                        'role': 'Local Orchestrator & IDE'
                    }
                }
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(status, indent=2).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server = HTTPServer(('0.0.0.0', BRIDGE_PORT), MeshBridgeHandler)
    LOG.info(f'Full Mesh Bridge active on port {BRIDGE_PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == '__main__':
    run_server()
