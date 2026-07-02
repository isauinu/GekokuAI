import os
import signal
from utils.globals import RUNTIME
from modules.stop_model import *
from utils.logger import *
from utils.endpoint_response import *

def stop_daemon():
    loaded_models = RUNTIME.running_models.keys()
    if loaded_models:
        for model in tuple(loaded_models):
            stop_model(model)
            verbose(f"model {model} has been stopped")
        success("All loaded models are stopped")
    daemon_pid = RUNTIME.pid
    if RUNTIME.running:
        info("Stopping Daemon")
        if daemon_pid:
            os.kill(daemon_pid, signal.SIGTERM)
            success("Signaled daemon to terminate")
            return return_response(
                True,
                "Daemon has been safely terminated"
            )

    else:
        error("The daemon is not running")