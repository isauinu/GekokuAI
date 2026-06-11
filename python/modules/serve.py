
from utils.logger import *
from utils.vars import GEKOKU_HOME, MODELS_DIR_PATH, CONFIG_DATA
from utils.toml_manager import *
from utils.daemon_cleanup import *
from pathlib import Path
import subprocess

def serve_model(args):
    info("Starting GekokuAI server...")
    for file in MODELS_DIR_PATH.iterdir():
        if file.is_file() and args.serve_model in file.name:
                log(f"Found model config: {file}")
                model_toml_path = file
    
    model_config = read_toml(model_toml_path)
    
    model_path = model_config["metadata"]["path"]
    model_mmproj_path = model_config["metadata"]["mmproj_path"]
    llama_cpp = (Path(CONFIG_DATA["llama_cpp"]["llama_cpp_path"])/"build"/"bin"/"llama-server")
    llama_args = model_config["arguments"]["llama_args"]
    server_host = CONFIG_DATA["server"]["host"]
    server_port = CONFIG_DATA["server"]["port"]
    
    launch_command = [str(llama_cpp), "-m", model_path]
    if model_mmproj_path:
        launch_command.append("--mmproj")
        launch_command.append(model_mmproj_path)
    if server_host:
        launch_command.append("--host")
        launch_command.append(server_host)
    if server_port:
        launch_command.append("--port")
        launch_command.append(server_port)
    if llama_args:
        parsed_args = llama_args.split()
        for arguments in parsed_args:
            launch_command.append(arguments)
    log(f"Final command form: {launch_command}")
    backend_server = subprocess.Popen(launch_command)
    runtime_data = {
        "server": {
            "running": True,
            "pid": backend_server.pid,
            "model": args.serve_model,
            "host": server_host or "127.0.0.1",
            "port": server_port or "8080"
        }
    }
    runtime_dir_path = Path(f"{GEKOKU_HOME}/runtime")
    if not runtime_dir_path.is_dir():
        warn("Runtime folder to store server information doesn't exist, creating one")
        runtime_dir_path.mkdir(parents=True, exist_ok=True)
    toml_path = runtime_dir_path / "runtime.toml"
    with open (toml_path, "wb") as toml_file:
        tomli_w.dump(runtime_data, toml_file)
    success("Successfully created runtime data")
    try:
        backend_server.wait()
    except:
        log("Program quits due to user intervention")
    finally:
        daemon_cleanup()