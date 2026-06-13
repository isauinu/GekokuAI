from pathlib import Path
from utils.toml_manager import *
from utils.vars import GEKOKUAI_VERSION, RUNTIME_DIR_PATH, RUNTIME_DAEMON_FILE_PATH, RUNTIME_DAEMON_DATA
from utils.logger import *
from utils.exception_handling import *

def status(args):
    status_running = RUNTIME_DAEMON_DATA["server"]["running"]
    status_pid = RUNTIME_DAEMON_DATA["server"]["pid"]
    status_model = RUNTIME_DAEMON_DATA["server"]["models"]
    status_host = RUNTIME_DAEMON_DATA["server"]["host"]
    status_port = RUNTIME_DAEMON_DATA["server"]["port"]
    log_file = RUNTIME_DAEMON_DATA["server"]["log_file"]

    print(f"GekokuAI Status:\n\nVersion: {GEKOKUAI_VERSION}\n\nRunning: {status_running}\nPID: {status_pid}\nLoaded models: {status_model}\nHost: {status_host}\nPort: {status_port}\nLog file: {log_file}")