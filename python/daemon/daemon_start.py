from utils.vars import GEKOKU_PROJECT_ROOT, CONFIG_DATA, RUNTIME_DIR_PATH, LOG_DIR_PATH
from utils.toml_manager import *
from utils.logger import *
from pathlib import Path
import subprocess
from datetime import datetime
from utils.check_port_availability import *
import requests

def start_daemon(args):
    info("Starting Gekoku daemon...")
    if args.host:
        server_host = args.host
    else:
        server_host = CONFIG_DATA["server"]["host"] or '127.0.0.1'
    if args.port:
        server_port = args.port
    else:
        server_port = CONFIG_DATA["server"]["port"] or 8080
    
    if check_if_port_used(server_port):
        response = requests.get(f"http://127.0.0.1:{server_port}/api/v1/health")
        if response:
            error("an existing Gekoku daemon is running in the background, aborting starting another one")
            fatal("Aborting...")
        else:
            error(f"A process already occupied port {server_port}. make sure that port is available to use")
            fatal("Aborting...")
    timestap_log = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_path = Path(LOG_DIR_PATH, f"{timestap_log}_gekoku.log")
    try:
        with open(log_file_path, "w") as file:
            file.write("Starting Gekoku daemon...\n")
    except FileExistsError:
        log("Log file already exists within the same time session")
    daemon_path = Path(GEKOKU_PROJECT_ROOT, "daemon", "gekokud.py")
    daemon_process = subprocess.Popen([sys.executable, str(daemon_path)], stdout=open(log_file_path, "a"), stderr=open(log_file_path, "a"))
    runtime_data = {
        "server": {
            "running": True,
            "pid": daemon_process.pid,
            "models": [],
            "host": server_host or "127.0.0.1",
            "port": server_port or 8080,
            "log_file": f"{log_file_path}"
        }
    }
    if not RUNTIME_DIR_PATH.is_dir():
        warn("Runtime folder to store server information doesn't exist, creating one")
        RUNTIME_DIR_PATH.mkdir(parents=True, exist_ok=True)
    toml_path = Path(RUNTIME_DIR_PATH, "runtime.toml")
    write_toml(toml_path, runtime_data)
    log("Successfully created runtime data")
    success(f"Gekoku daemon has successfully been run (PID: {daemon_process.pid})")