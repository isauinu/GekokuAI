import socket
from utils.globals import CONFIG_DATA 
from utils.logger import *
import traceback

def get_unused_port(start_port):
    try:
        while start_port <= 65536:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', start_port))
                    return start_port
                except socket.error:
                    start_port += 1
        raise IOError("No free ports are available in range.")
    except Exception as e:
        error(f"An error occured: {e}")
        verbose(traceback.format_exc())
        fatal("exiting...")

def check_if_port_used(port: int) -> bool:
    host = CONFIG_DATA["server"]["host"] or '127.0.0.1'
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((host, port)) == 0
    except Exception as e:
        error(f"An error occured: {e}")
        verbose(traceback.format_exc())
        fatal("exiting...")