from pathlib import Path
from utils.toml_manager import *
from utils.vars import GEKOKUAI_VERSION, RUNTIME_DIR_PATH
from utils.logger import *

def status(args):
    if not RUNTIME_DIR_PATH.is_dir():
        warn("Runtime folder to store server information doesn't exist, creating one")
        RUNTIME_DIR_PATH.mkdir(parents=True, exist_ok=True)

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
    status_running = runtime_file["server"]["running"]
    status_pid = runtime_file["server"]["pid"]
    status_model = runtime_file["server"]["model"]
    status_host = runtime_file["server"]["host"]
    status_port = runtime_file["server"]["port"]
    
    print(f"GekokuAI Status:\n\nVersion: {GEKOKUAI_VERSION}\n\nRunning: {status_running}\nPID: {status_pid}\nLoaded model: {status_model}\nHost: {status_host}\nPort: {status_port}")