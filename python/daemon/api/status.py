from fastapi import APIRouter
from utils.logger import *
from utils.globals import API_PREFIX, RUNTIME
from utils.runtime_inspection import check_runtime

router = APIRouter(prefix=API_PREFIX)

@router.get("/status")
def read_status():
    runtime_model = {}
    for running_instance in RUNTIME.running_models.values():
        runtime_model[running_instance.model] = {
            "pid": running_instance.pid,
            "port": running_instance.port
        }
    status_running = RUNTIME.running
    status_pid = RUNTIME.pid
    status_model = runtime_model
    status_host = RUNTIME.host
    status_port = RUNTIME.port
    status_log_file = RUNTIME.log_file
    return {
        "running": status_running,
        "pid": status_pid,
        "models": status_model,
        "host": status_host,
        "port": status_port,
        "log_file": status_log_file
    }