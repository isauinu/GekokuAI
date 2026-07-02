from utils.globals import GEKOKU_PROJECT_ROOT, CONFIG_DATA, RUNTIME_DIR_PATH, LOG_DIR_PATH, RUNTIME, RUNTIME_SNAPSHOT
from utils.toml_manager import *
from utils.logger import *
from pathlib import Path
import subprocess
from datetime import datetime
from utils.check_port_availability import *
from utils.daemon_cleanup import *
import requests
from modules.serve import *
from utils.runtime_inspection import wait_until_ready
import os

def start_daemon(args):
    info("Starting Gekoku daemon...")
    if args.host:
        server_host = args.host
        verbose(f"server host overwritten to {args.host}")
    else:
        server_host = CONFIG_DATA["server"]["host"] or '127.0.0.1'
    if args.port:
        server_port = args.port
        verbose(f"server port overwritten to {args.port}")
    else:
        server_port = CONFIG_DATA["server"]["port"] or 8080
    
    if check_if_port_used(server_port):
        response = requests.get(f"http://127.0.0.1:{server_port}/api/v1/health")
        if response and RUNTIME_SNAPSHOT["server"]["running"]:
            error("an existing Gekoku daemon is running in the background, aborting starting another one")
            fatal("Aborting...")
        else:
            error(f"A process already occupied port {server_port}. make sure that port is available to use")
            fatal("Aborting...")
    timestap_log = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_path = Path(LOG_DIR_PATH, f"{timestap_log}_gekoku.log")
    verbose(f"Daemon started at timestamp {timestap_log}")
    verbose(f"Log file name: {log_file_path}")
    try:
        with open(log_file_path, "w") as file:
            file.write("Starting Gekoku daemon...\n")
    except FileExistsError:
        log("Log file already exists within the same time session")
    daemon_path = Path(GEKOKU_PROJECT_ROOT, "daemon", "gekokud.py")
    daemon_process = subprocess.Popen(
        [sys.executable, str(daemon_path)], 
        stdout=open(log_file_path, "a"), 
        stderr=open(log_file_path, "a"),
        env={
            **os.environ,
            "GEKOKU_HOST": str(server_host) or "127.0.0.1",
            "GEKOKU_PORT": str(server_port) or str(8080),
            "GEKOKU_LOG_FILE": str(log_file_path)
        }
    )
    RUNTIME.running = True
    RUNTIME.process = daemon_process
    RUNTIME.pid = daemon_process.pid
    RUNTIME.host = server_host or "127.0.0.1"
    RUNTIME.port = server_port or 8080
    RUNTIME.log_file = log_file_path
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
    verbose(f"Runtime data content: {runtime_data}")
    if not RUNTIME_DIR_PATH.is_dir():
        warn("Runtime folder to store server information doesn't exist, creating one")
        RUNTIME_DIR_PATH.mkdir(parents=True, exist_ok=True)
    toml_path = Path(RUNTIME_DIR_PATH, "runtime.toml")
    write_toml(toml_path, runtime_data)
    log("Successfully created runtime data")
    verbose(f"runtime in memory: {RUNTIME}")
    verbose(f"runtime structure {RUNTIME.__dict__}")
    if wait_until_ready(daemon_process, server_port):
        print(f"[{datetime.now()}]")
        print(f"GekokuAI {GEKOKUAI_VERSION}\n")
        print(f"{"Detail":<15} | Daemon has been successfully started! (PID {daemon_process.pid})")
        print(f"{"Daemon host":<15} | {server_host}")
        print(f"{"Daemon port":<15} | {server_port}\n")
        print("Run `gekoku logs` to see the log of the daemon in real time")
    else:
        error(f"An error occured while trying to start up the daemon, check the latest log located in {log_file_path}")
        daemon_cleanup()
    if (args.serve_model):
        log(f"Launching model {args.serve_model}")
        if wait_until_ready(daemon_process, server_port):
            load_data = {
                "model": args.serve_model
            }
            response = requests.post(f"http://127.0.0.1:{server_port}/api/v1/load", json=load_data)
            parse_response(response)