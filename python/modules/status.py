from pathlib import Path
from utils.toml_manager import *
from utils.vars import GEKOKUAI_VERSION, RUNTIME_DIR_PATH, RUNTIME_DAEMON_FILE_PATH, RUNTIME_DAEMON_DATA
from utils.logger import *
from utils.exception_handling import *

def status(args):
    if not check_dir_exists(RUNTIME_DIR_PATH):
        warn("Runtime folder to store server information doesn't exist, creating one")
        RUNTIME_DIR_PATH.mkdir(parents=True, exist_ok=True)

    if not check_file_exists(RUNTIME_DAEMON_FILE_PATH):
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
        write_toml(RUNTIME_DAEMON_FILE, runtime_data)

    status_running = RUNTIME_DAEMON_DATA["server"]["running"]
    status_pid = RUNTIME_DAEMON_DATA["server"]["pid"]
    status_model = RUNTIME_DAEMON_DATA["server"]["model"]
    status_host = RUNTIME_DAEMON_DATA["server"]["host"]
    status_port = RUNTIME_DAEMON_DATA["server"]["port"]
    
    print(f"GekokuAI Status:\n\nVersion: {GEKOKUAI_VERSION}\n\nRunning: {status_running}\nPID: {status_pid}\nLoaded model: {status_model}\nHost: {status_host}\nPort: {status_port}")