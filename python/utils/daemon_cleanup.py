import sys
from utils.logger import *
from utils.vars import RUNTIME_DAEMON_FILE_PATH
from utils.toml_manager import *
from pathlib import Path

def daemon_cleanup(signum=None, frame=None):
    log(f"Programs quit due to external intervention (Recieved signal: {signum}), exiting...")
    log(f"Cleaning up runtime information")
    runtime_data = {
        "server": {
            "running": False,
            "pid": 0,
            "models": [],
            "host": "",
            "port": "",
            "log_file": ""
        }
    }
    write_toml(RUNTIME_DAEMON_FILE_PATH, runtime_data)
    success("Program has been terminated")
    sys.exit(0)