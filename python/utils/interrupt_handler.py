import signal
from utils.logger import *

def handler(signum=None, frame=None):
    error(f"Recieved signal to quit: {signum}")
    fatal("Aborting...")

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)