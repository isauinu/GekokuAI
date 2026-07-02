from utils.toml_manager import *
from utils.logger import *
import os
import signal
from utils.globals import RUNTIME
from utils.llama_cleanup import *
from utils.endpoint_response import *

def stop_model(model):
    if RUNTIME.running:
        info(f"Stopping model {model}...")
        if model in RUNTIME.running_models.keys():
            pid = RUNTIME.running_models[model].pid
            if pid:
                try:
                    os.kill(pid, signal.SIGTERM)
                    success(f"Server for model {model} succesfully killed. PID {pid}")
                except ProcessLookupError:
                    error(f"No process found with PID: {pid}")
                except OSError as e:
                    error(f"No process found with PID: {pid} (Error: {e})")
                llama_cleanup(model)
                del RUNTIME.running_models[model]
                verbose(RUNTIME.__dict__)
                return return_response(
                    True,
                    f"Server for model {model} succesfully killed. PID {pid}",
                    model = model
                )
        else:
            error(f"Unable to find model with the name {model}")
            return return_response(
                False,
                f"Unable to find model with the name {model}",
                model = model
            )
    else:
        error("Gekoku daemon is not running")