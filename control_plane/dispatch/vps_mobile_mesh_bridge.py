# SPDX-License-Identifier: MIT
import sys, json, os, urllib.request, logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s')
LOG = logging.getLogger('VpsMobileMeshBridge')

VPS_TAILSCALE_IP = os.getenv('VPS_TAILSCALE_IP', '100.71.218.75')
MOBILE_TAILSCALE_IP = os.getenv('MOBILE_TAILSCALE_IP', '100.106.246.126')
LOCAL_BIFROST_PORT = int(os.getenv('BIFROST_PORT', 3001))
BRIDGE_PORT = int(os.getenv('VPS_BRIDGE_PORT', 8095))

class MeshBridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/mesh/status', '/']:
            status = {
                'mesh_status': 'ONLINE',
                'topology': {
                    'vps_node': VPS_TAILSCALE_IP,
                    'mobile_sentinel': MOBILE_TAILSCALE_IP,
                    'bifrost_host': '100.118.224.52',
                    'active_ports': {
                        'mobile_node': 8090,
                        'mobile_ssh': 8022,
                        'bifrost': LOCAL_BIFROST_PORT,
                        'bridge': BRIDGE_PORT
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
    LOG.info(f'VPS <-> Mobile Mesh Bridge active on port {BRIDGE_PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == '__main__':
    run_server()
