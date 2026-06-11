import sys
from utils.logger import *
from utils.vars import RUNTIME_DIR_PATH
from utils.toml_manager import *
from pathlib import Path

def daemon_cleanup(signum=None, frame=None):
    log(f"Programs quit due to external intervention (Recieved signal: {signum}), exiting...")
    runtime_file_path = Path(f"{RUNTIME_DIR_PATH}", "runtime.toml")
    log(f"Cleaning up runtime information")
    runtime_data = {
        "server": {
            "running": False,
            "pid": 0,
            "model": "",
            "host": "",
            "port": ""
        }
    }
    write_toml(runtime_file_path, runtime_data)
    success("Program has been terminated")
    sys.exit(0)