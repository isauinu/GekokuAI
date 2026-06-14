import os
import signal
from utils.vars import RUNTIME_DAEMON_DATA
from modules.stop_model import *
from utils.logger import *

def stop_daemon():
    info("Stopping Daemon")
    loaded_models = RUNTIME_DAEMON_DATA["server"]["models"]
    if loaded_models:
        for model in loaded_models:
            stop_model(model)
            log(f"model {model} has been stopped")
        success("All loaded models are stopped")
    daemon_pid = RUNTIME_DAEMON_DATA["server"]["pid"]
    if RUNTIME_DAEMON_DATA["server"]["running"]:
        if daemon_pid:
            os.kill(daemon_pid, signal.SIGTERM)
            success("Signaled daemon to terminate")
    else:
        error("The daemon is not running")