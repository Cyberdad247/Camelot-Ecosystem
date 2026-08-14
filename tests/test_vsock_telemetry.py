# SPDX-License-Identifier: MIT

import socket
import threading
import time
import unittest


class TestVsockTelemetry(unittest.TestCase):
    def test_mock_vsock_telemetry_flow(self):
        # 1. Start Go vsock_multiplexer emulator (TCP port 1024 fallback)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("127.0.0.1", 1024))
        server_socket.listen(1)

        received_data = []

        def serve():
            try:
                conn, addr = server_socket.accept()
                data = conn.recv(1024)
                received_data.append(data)
                conn.sendall(b"ACK")
                conn.close()
            except Exception:
                pass

        t = threading.Thread(target=serve)
        t.start()

        # 2. Connect client and transmit payload
        time.sleep(0.05)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 1024))
        client_socket.sendall(b"PILL_TELEMETRY: STATUS=OK")
        
        ack = client_socket.recv(1024)
        client_socket.close()

        # 3. Stop server and assert results
        server_socket.close()
        t.join()

        self.assertEqual(received_data[0], b"PILL_TELEMETRY: STATUS=OK")
        self.assertEqual(ack, b"ACK")

if __name__ == "__main__":
    unittest.main()
