import socket
from utils.vars import CONFIG_DATA 

def get_unused_port(start_port):
    while start_port <= 65536:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', start_port))
                return start_port
            except socket.error:
                start_port += 1
    raise IOError("No free ports are available in range.")

def check_if_port_used(port: int) -> bool:
    host = CONFIG_DATA["server"]["host"] or '127.0.0.1'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0