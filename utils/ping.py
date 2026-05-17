def ping(host):
    try:
        socket.create_connection((host, 80))
        return True
    except:
        return False
