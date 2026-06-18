from ast import Pass
import time
from utils.logger import *
from utils.vars import get_daemon_data
import os
from utils.llama_cleanup import *
import psutil

import requests

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
    RUNTIME_DAEMON_DATA = get_daemon_data()
    models_list = RUNTIME_DAEMON_DATA["server"]["models"]
    for model in models_list:
        pid = RUNTIME_DAEMON_DATA[model]["pid"]
        if not psutil.pid_exists(pid):
            llama_cleanup(model)
        else:
            Pass