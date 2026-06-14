from fastapi import APIRouter
from utils.logger import *
from utils.vars import API_PREFIX, RUNTIME_DAEMON_DATA

router = APIRouter(prefix=API_PREFIX)

@router.get("/status")
def read_status():
    log("Recieved signal")
    status_running = RUNTIME_DAEMON_DATA["server"]["running"]
    status_pid = RUNTIME_DAEMON_DATA["server"]["pid"]
    status_model = RUNTIME_DAEMON_DATA["server"]["models"]
    status_host = RUNTIME_DAEMON_DATA["server"]["host"]
    status_port = RUNTIME_DAEMON_DATA["server"]["port"]
    status_log_file = RUNTIME_DAEMON_DATA["server"]["log_file"]
    return {
        "status": "ok",
        "running": status_running,
        "PID": status_pid,
        "models": status_model,
        "host": status_host,
        "port": status_port,
        "log_file": status_log_file
    }