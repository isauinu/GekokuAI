from utils.toml_manager import *
from utils.globals import GEKOKUAI_VERSION, RUNTIME_SNAPSHOT
from utils.logger import *
from utils.exception_handling import *
import requests

def status(args):
    try:
        response = requests.get(f"http://127.0.0.1:{RUNTIME_SNAPSHOT["server"]["port"]}/api/v1/status")
    except requests.exceptions.ConnectionError:
        error("The daemon is not running")
        return
    except requests.exceptions.Timeout:
        error("The request timed out. Daemon is taking too long to response")
        return
    except requests.exceptions.TooManyRedirects:
        error("Too many redirects on the following endpoint")
        return
    except requests.exceptions.RequestException as e:
        error(f"An unexpected error had occured: {e}")
        return
    status_data = response.json()

    center_span = 41
    width_span = 15

    print(f"[{datetime.now()}]")
    print(f"GekokuAI {GEKOKUAI_VERSION}\n")
    print(f"{"Status":-^{center_span}}")
    print(f"{"Running":<{width_span}}|  {str(status_data["running"])}")
    print(f"{"PID":<{width_span}}|  {str(status_data["pid"])}")
    print(f"{"Loaded models":<{width_span}}|  {len(status_data["models"])}")
    print(f"{"Host":<{width_span}}|  {str(status_data["host"])}")
    print(f"{"Port":<{width_span}}|  {str(status_data["port"])}")
    print(f"{"Log file":<{width_span}}|  {str(status_data["log_file"])}")
    
    print()

    for key, value in status_data["models"].items():
        print(f"{key:-^{center_span}}")
        print(f"{"PID":<{width_span}}|  {str(value["pid"])}")
        print(f"{"Port":<{width_span}}|  {str(value["port"])}")
        print()