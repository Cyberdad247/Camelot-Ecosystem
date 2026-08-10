import socket
def ping(host):
    try:
        socket.create_connection((host, 80))
        return True
    except Exception:
        return False

