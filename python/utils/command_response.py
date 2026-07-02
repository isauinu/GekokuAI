import requests
from utils.logger import *
from typing import Literal
from utils.globals import RUNTIME_SNAPSHOT
from utils.endpoint_response import *

def send_request(method: Literal["get", "post",  "put", "delete"], endpoint, id = None, body = None):
    daemon_port = RUNTIME_SNAPSHOT["server"]["port"] or 8080
    daemon_check = None
    try:
        daemon_check = requests.get(f"http://127.0.0.1:{daemon_port}/api/v1/health")
    except requests.exceptions.ConnectionError:
        pass
    if not daemon_check:
        error("The daemon is not running")
        return

    if id:
        url = f"http://127.0.0.1:{daemon_port}/api/v1/{endpoint}?id={id}"
    else:
        url = f"http://127.0.0.1:{daemon_port}/api/v1/{endpoint}"
    try:
        match method:
            case "get":
                response = requests.get(url)
                parse_response(response)
            case "post":
                response = requests.post(url, json=body)
                parse_response(response)
            case "put":
                response = requests.put(url, json=body)
                parse_response(response)
            case "delete":
                response = requests.delete(url)
                parse_response(response)
    except requests.exceptions.ConnectionError:
        error("Network error occured. Check to make sure if daemon is still running")
    except requests.exceptions.Timeout:
        error("The request timed out. Daemon is taking too long to response")
    except requests.exceptions.TooManyRedirects:
        error("Too many redirects on the following endpoint")
    except requests.exceptions.RequestException as e:
        error(f"An unexpected error had occured: {e}")