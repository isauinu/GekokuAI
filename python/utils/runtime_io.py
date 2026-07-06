from utils.logger import *
from utils.globals import RUNTIME, RUNTIME_DIR_PATH, RUNTIME_SNAPSHOT_FILE_PATH
from utils.toml_manager import *
from pathlib import Path

def runtime_save(model = None, pid = None, port = None):
    runtime_model = []
    for running_instance in RUNTIME.running_models.values():
        runtime_model.append(running_instance.model)
    runtime_data = {
        "server": {
            "running": RUNTIME.running,
            "pid": RUNTIME.pid,
            "models": runtime_model,
            "host": RUNTIME.host,
            "port": RUNTIME.port,
            "log_file": f"{RUNTIME.log_file}"
        }
    }

    if model and pid and port:
        runtime_data[model] = {
            "pid": pid,
            "port": port
        }
    if not RUNTIME_DIR_PATH.is_dir():
        error("Runtime folder to store server information doesn't exist")
    write_toml(RUNTIME_SNAPSHOT_FILE_PATH, runtime_data)

def runtime_load():
    return read_toml(RUNTIME_SNAPSHOT_FILE_PATH)