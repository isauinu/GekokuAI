from ast import Pass
import time
from utils.logger import *
from utils.globals import RUNTIME
from utils.llama_cleanup import *
from utils.runtime_io import *
import requests
import threading

def wait_until_ready(launch_process, port):
    timeout = 60
    start = time.time()
    info("Verifying server runtime")
    while time.time() - start < timeout:
        if launch_process.poll() is not None:
            error("A problem has occured during server initialization")
            return False
        try:
            requests.get(
                f"http://localhost:{port}/api/v1/health",
                timeout=1
            )
            success("Server has successfully started properly")
            return True
        except:
            Pass
        time.sleep(1)
    error("Server takes too long too load")
    return False

def check_runtime():
    while RUNTIME.running:
        for model in list(RUNTIME.running_models.values()):
            if model.process.poll() is not None:
                warn(f"{model.model} has unexpectedly stopped! terminating model safely")
                llama_cleanup(model.model)
                del RUNTIME.running_models[model.model]
                runtime_save()
        time.sleep(1)

def start_runtime_monitor():
    threading.Thread(
        target=check_runtime,
        daemon=True
    ).start()