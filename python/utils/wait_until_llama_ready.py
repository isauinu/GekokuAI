
from ast import Pass
import time

import requests


def wait_until_ready(launch_process, port):
    timeout = 60

    start = time.time()

    while time.time() - start < timeout:
        if launch_process.poll() is not None:
            return False
    
        try:
            requests.get(
                f"https://127.0.0.1:{port}/api/v1/health",
                timeout=1
            )
            return True
        except:
            Pass
        
        time.sleep(1)
    return False