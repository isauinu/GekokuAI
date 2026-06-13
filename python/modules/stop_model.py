from utils.toml_manager import *
from utils.logger import *
import os
import signal
from utils.vars import RUNTIME_DAEMON_DATA
from utils.llama_cleanup import *

def stop_model(model):
    info(f"Stopping model {model}...")
    pid = RUNTIME_DAEMON_DATA[model]["pid"]
    if pid:
        os.kill(pid, signal.SIGTERM)
        success(f"Server for model {model} succesfully killed. PID {pid}")
        llama_cleanup(model)
    else:
        error(f"Unable to find model with the name {model}...")