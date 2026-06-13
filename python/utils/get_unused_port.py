import socket

def get_unused_port(start_port):
    while start_port <= 65536:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', start_port))
                return start_port
            except socket.error:
                start_port += 1
    raise IOError("No free ports are available in range.")
