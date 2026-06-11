from utils.toml_manager import *
from utils.logger import *
from pathlib import Path
import os
import signal
from utils.vars import RUNTIME_DIR_PATH

def stop_model_serve(args):
    info("Stopping GekokuAI server...")
    runtime_file_path = Path(f"{RUNTIME_DIR_PATH}", "runtime.toml")
    if not runtime_file_path.is_file():
        warn("Runtime file not found, creating a default inactive runtime information")
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
    runtime_file = read_toml(runtime_file_path)
    status_pid = runtime_file["server"]["pid"]
    if status_pid != 0:
        os.kill(status_pid, signal.SIGTERM)
        success(f"Server succesfully killed. PID {status_pid}")
    else:
        error("There's no server to stop...")