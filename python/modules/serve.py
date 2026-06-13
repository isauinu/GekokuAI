
from utils.logger import *
from utils.vars import MODELS_DIR_PATH, CONFIG_DATA, RUNTIME_DIR_PATH, RUNTIME_DAEMON_DATA, RUNTIME_DAEMON_FILE_PATH
from utils.toml_manager import *
from pathlib import Path
import subprocess
from utils.exception_handling import *
from utils.get_unused_port import *

def launch_model(launch_model):
    if check_model_exists(launch_model):
        info("Starting GekokuAI instance...")
        for file in MODELS_DIR_PATH.iterdir():
            if file.is_file() and launch_model in file.name:
                    log(f"Found model config: {file}")
                    model_toml_path = file
        
        model_config = read_toml(model_toml_path)
        
        model_path = model_config["metadata"]["path"]
        model_mmproj_path = model_config["metadata"]["mmproj_path"]
        llama_cpp = Path(CONFIG_DATA["llama_cpp"]["llama_cpp_path"], "build", "bin", "llama-server")
        llama_args = model_config["arguments"]["llama_args"]
        server_host = CONFIG_DATA["server"]["host"]
        config_port = CONFIG_DATA["server"]["port"]
        server_port = get_unused_port(config_port)
        
        launch_command = [str(llama_cpp), "-m", model_path, "--port", str(server_port)]
        if model_mmproj_path:
            launch_command.append("--mmproj")
            launch_command.append(model_mmproj_path)
        if server_host:
            launch_command.append("--host")
            launch_command.append(server_host)
        if llama_args:
            parsed_args = llama_args.split()
            for arguments in parsed_args:
                launch_command.append(arguments)
        log(f"Final command form: {launch_command}")
        launch_process = subprocess.Popen(launch_command)
        RUNTIME_DAEMON_DATA[launch_model] = {
            "pid": launch_process.pid,
            "port": server_port
        }
        RUNTIME_DAEMON_DATA["server"]["models"].append(launch_model)
        if not RUNTIME_DIR_PATH.is_dir():
            warn("Runtime folder to store server information doesn't exist, creating one")
            RUNTIME_DIR_PATH.mkdir(parents=True, exist_ok=True)
        write_toml(RUNTIME_DAEMON_FILE_PATH, RUNTIME_DAEMON_DATA)
        return success("Successfully created runtime data")
    else:
        error("Unable to start model because model with that name does not exist")