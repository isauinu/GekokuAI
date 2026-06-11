
from utils.logger import *
from utils.vars import MODELS_DIR_PATH, CONFIG_DATA, RUNTIME_DIR_PATH
from utils.toml_manager import *
from utils.daemon_cleanup import *
from pathlib import Path
import subprocess
from utils.exception_handling import *

def serve_model(args):
    if check_model_exists(args.serve_model):
        info("Starting GekokuAI instance...")
        for file in MODELS_DIR_PATH.iterdir():
            if file.is_file() and args.serve_model in file.name:
                    log(f"Found model config: {file}")
                    model_toml_path = file
        
        model_config = read_toml(model_toml_path)
        
        model_path = model_config["metadata"]["path"]
        model_mmproj_path = model_config["metadata"]["mmproj_path"]
        llama_cpp = Path(CONFIG_DATA["llama_cpp"]["llama_cpp_path"], "build", "bin", "llama-server")
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
        if not RUNTIME_DIR_PATH.is_dir():
            warn("Runtime folder to store server information doesn't exist, creating one")
            RUNTIME_DIR_PATH.mkdir(parents=True, exist_ok=True)
        toml_path = Path(RUNTIME_DIR_PATH, "runtime.toml")
        write_toml(toml_path, runtime_data)
        success("Successfully created runtime data")
        try:
            backend_server.wait()
        except:
            log("Program quits due to user intervention")
        finally:
            daemon_cleanup()
    else:
        error("Unable to start model because model with that name does not exist")