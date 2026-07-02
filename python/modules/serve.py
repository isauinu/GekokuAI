
from utils.runtime_inspection import *
from utils.logger import *
from utils.globals import MODELS_DIR_PATH, CONFIG_DATA, RUNTIME, RUNTIME_SNAPSHOT
from utils.toml_manager import *
from pathlib import Path
import subprocess
from utils.exception_handling import *
from utils.check_port_availability import *
from utils.runtime import RunningModel
from utils.runtime_io import *
from utils.endpoint_response import *
import pprint

def launch_model(launch_model):
    if RUNTIME_SNAPSHOT["server"]["running"]:
        if check_model_exists(launch_model):
            info("Starting GekokuAI instance...")

            if launch_model in RUNTIME.running_models.keys():
                error("Model with that name already started")
                return return_response(
                    False,
                    "Model with that name already started",
                    model = launch_model
                )
            
            log_file_path = RUNTIME.log_file

            model_toml_path = None
            for file in MODELS_DIR_PATH.iterdir():  
                verbose(file)
                if file.is_file() and launch_model in file.name:
                        log(f"Found model config: {file}")
                        model_toml_path = file
            
            if not model_toml_path:
                error(f"Unable to find the config file for model {launch_model}")
                return return_response(
                    False,
                    f"Unable to find the config file for model {launch_model}",
                    model = launch_model
                )
            model_config = read_toml(model_toml_path)

            verbose(f"Runtime id {id(RUNTIME)}")
            verbose(f"Runtime host {RUNTIME.host}")
            verbose(f"Runtime port {RUNTIME.port}")
            verbose(f"runtime in memory: {RUNTIME}")
            verbose(f"runtime structure: {RUNTIME.__dict__}")
            
            model_path = model_config["metadata"]["path"]
            model_mmproj_path = model_config["metadata"]["mmproj_path"]
            model_capabilities = model_config["metadata"]["capabilities"]
            llama_cpp = Path(CONFIG_DATA["llama_cpp"]["llama_cpp_path"], "build", "bin", "llama-server")
            llama_args = model_config["arguments"]["llama_args"]
            server_host = RUNTIME.host
            config_port = RUNTIME.port
            server_port = get_unused_port(config_port)
            
            verbose(f"Model capabilities: {model_capabilities}")
            verbose(f"Model llama arguments: {llama_args}")
            
            launch_command = [str(llama_cpp), "-m", model_path, "--port", str(server_port)]
            if server_host:
                launch_command.append("--host")
                launch_command.append(server_host)
            if model_mmproj_path and "vision" in model_capabilities:
                launch_command.append("--mmproj")
                launch_command.append(model_mmproj_path)
            if "embedding" in model_capabilities:
                launch_command.append("--embedding")
            if "reranking" in model_capabilities:
                launch_command.append("--reranking")
            if llama_args:
                parsed_args = llama_args.split()
                for arguments in parsed_args:
                    launch_command.append(arguments)
            log(f"Final command form: {launch_command}")
            launch_process = subprocess.Popen(launch_command, stdout=open(log_file_path, "a"), stderr=open(log_file_path, "a"))
            if wait_until_ready(launch_process, server_port):
                running_model = RunningModel()
                running_model.model = launch_model
                running_model.process = launch_process
                running_model.pid = launch_process.pid
                running_model.port = server_port
                RUNTIME.running_models[launch_model] = running_model
                runtime_save(launch_model, launch_process.pid, server_port)
                verbose(f"runtime structure\n {pprint.pprint(RUNTIME.__dict__)}")
                info("created model runtime data in the snapshot")
                success("Server of the model has been successfully started")
                return return_response(
                    True,
                    "Server of the model has been successfully started",
                    model = launch_model,
                    model_pid = launch_process.pid,
                    model_port = server_port
                )
            else:
                error("Unable to start model due to an error, please check logs")
                return return_response(
                    False,
                    "Unable to start model due to an error, please check logs",
                    model = launch_model
                )
        else:
            error("Unable to start model because model with that name does not exist")
            return return_response(
                    False,
                    "Unable to start model because model with that name does not exist",
                    model = launch_model
                )
    else:
        error("Gekoku daemon is not running")