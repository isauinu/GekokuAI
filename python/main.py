#!/usr/bin/env python3
import sys
import os
VENV_PYTHON = os.path.expanduser("~/.gekokuai/venv/bin/python")
if sys.executable != VENV_PYTHON:
    if not os.path.exists(VENV_PYTHON):
        fatal(f"Virtual environment for GekokuAI not found")
    os.execv(VENV_PYTHON, [VENV_PYTHON] + sys.argv)

#Actual part of the code here
import argparse
import tomllib
import tomli_w
from modules.logger import *
import subprocess
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download
import signal


version = "Alpha 0.1"

HOME = os.getenv('HOME')
with open(f"{HOME}/.gekokuai/config/config.toml", "rb") as f:
    config = tomllib.load(f)

GEKOKU_HOME = config["location"]["workspace"]

def cleanup(signum=None, frame=None):
    log(f"Programs quit due to external intervention (Recieved signal: {signum}), exiting...")
    runtime_file_path = Path(f"{GEKOKU_HOME}/runtime/runtime.toml")
    log(f"Cleaning up runtime information")
    runtime_data = {
        "server": {
            "running": False,
            "pid": 0,
            "model": "",
            "host": "",
            "port": ""
        }
    }
    with open (runtime_file_path, "wb") as toml_file:
        tomli_w.dump(runtime_data, toml_file)
    success("Program has been terminated")
    sys.exit(0)
signal.signal(signal.SIGTERM, cleanup)

def main():
    parser = argparse.ArgumentParser(description="Gekoku Backend command")
    subparser = parser.add_subparsers(dest="command", required=True)

    #info subcommand
    parser_info = subparser.add_parser("info", description="Displays the current GekokuAI Information")

    #doctor subcommand
    parser_doctor = subparser.add_parser("doctor", description="Displays the current state of the GekokuAI")

    #pull subcommand
    parser_pull = subparser.add_parser("pull", description="Pulls a model from huggingface")
    parser_pull.add_argument("pull_model", type=str, help="The model ID from Hugging face")
    parser_pull.add_argument("-q", "--quantization", type=str, required=False, help="Define download quantization", choices=[
    'Q2_K', 'Q2_K_S', 'Q2_K_M', 'Q2_K_L',
    'Q3_K_S', 'Q3_K_M', 'Q3_K_L',
    'Q4_0', 'Q4_1', 'Q4_K', 'Q4_K_S', 'Q4_K_M',
    'Q5_0', 'Q5_1', 'Q5_K', 'Q5_K_S', 'Q5_K_M',
    'Q6_K',
    'Q8_0', 'Q8_K',
    'IQ1_S', 'IQ1_M',
    'IQ2_XXS', 'IQ2_XS', 'IQ2_S', 'IQ2_M',
    'IQ3_XXS', 'IQ3_XS', 'IQ3_S', 'IQ3_M',
    'IQ4_NL', 'IQ4_XS',
    'FP16', 'BF16', 'FP32'
    ])
    parser_pull.add_argument("--embeddings", action="store_true", help="Indicates that the model is an embedding model")

    #serve subcommand
    parser_pull = subparser.add_parser("serve", description="Run llama.cpp backend")
    parser_pull.add_argument("serve_model", help="Which model to run?", type=str)
    parser_pull.add_argument("--host", help="Where to host?", type=str)
    parser_pull.add_argument("--port", help="Where from port?", type=int)

    #status subcommand
    parser_status = subparser.add_parser("status", description="Describes the status of the currently running backend")

    #list subcommand
    parser_list = subparser.add_parser("list", description="Lists everysingle models downloaded from huggingface")

    #remove subcommand
    parser_remove = subparser.add_parser("remove", description="Remove the selected downloaded model")
    parser_remove.add_argument("remove_model", help="Which model to remove?")

    #load subcommand (TODO)
    # parser_run = subparser.add_parser("load", description="load a downloaded model from huggingface")
    # parser_run.add_argument("load_model", help="Which model to load")

    #unload subcommand (TODO)
    # parser_run = subparser.add_parser("unload", description="load a downloaded model from huggingface")
    # parser_run.add_argument("load_model", help="Which model to unload")

    #stop subcommand
    parser_stop = subparser.add_parser("stop", description="Stops the currently running Gekoku Backend")

    args = parser.parse_args()

    #catch any methods to kill this... thing

    if args.command == "info":
        print("GekokuAI\n" + version + "\n")
    
    if args.command == "doctor":
        print("GekokuAI Doctor\n")
        cpu_backend = config["metadata"]["CPU_BACKEND"]
        gpu_backend = config["metadata"]["GPU_BACKEND"]
        cpu_name = subprocess.run("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs", shell=True, capture_output=True, text=True)
        if gpu_backend == "CUDA":
            gpu_parse = subprocess.run(r"""lspci | grep -i "VGA\|3d" | grep -i "NVIDIA" | sed 's/.*\[//;s/\].*//' | head -n 1""", shell=True, capture_output=True, text=True)
        elif gpu_backend == "ROCm":
            gpu_parse = subprocess.run(r"""lspci | grep -i "VGA\|3d" | grep -i "AMD" | sed 's/.*\[//;s/\].*//' | head -n 1""", shell=True, capture_output=True, text=True)
        else:
            gpu_parse = "-"

        if gpu_parse == "-":
            gpu_name = "-"
        else:
            gpu_name = gpu_parse.stdout
        ram = subprocess.run(r"""free -m | awk '/^Mem:/{print $2}' | sed 's/Gi//'""", shell=True, capture_output=True, text=True)
        swap = subprocess.run(r"""free -m | awk '/^Swap:/{print $2}' | sed 's/Gi//'""", shell=True, capture_output=True, text=True)
        storage = subprocess.run(r"""df -m / | awk 'NR==2 {print $2}'""", shell=True, capture_output=True, text=True)
        used_storage = subprocess.run(r"""df -m / | awk 'NR==2 {print $3}'""", shell=True, capture_output=True, text=True)
        cpu_flags = subprocess.run(r"""grep -m 1 "flags" /proc/cpuinfo""", shell=True, capture_output=True, text=True)
        print(f"CPU: {cpu_name.stdout}\nGPU: {gpu_name}\nCPU Backend: {cpu_backend}\nGPU Backend: {gpu_backend}\nRam: {ram.stdout}\nSwap: {swap.stdout}\nStorage: {storage.stdout}\nUsed: {used_storage.stdout}\nCPU Flags: {cpu_flags.stdout}")
    
    if args.command == "pull":
        info("Starting model pull from hugging face")
        api = HfApi()
        files = api.list_repo_files(repo_id=f"{args.pull_model}")
        model_target_file = None
        mmproj_target_file = None
        log(f"Found the following files in {args.pull_model}:")
        #Get model file
        for file in files:
            print(file, end=", ")
            #Get model when quantization is specified
            if args.quantization:
                if args.quantization in file and not "mmproj" in file:
                    log(f"Found model file: {file}")
                    model_target_file = file
                if args.quantization in file and "mmproj" in file:
                    log(f"Found mmproj file: {file}")
                    mmproj_target_file = file
            #if no quantization specified, Get Q4_K_M by default
            elif "Q4_K_M" in file and not "mmproj" in file:
                log(f"Found model file: {file}")
                model_target_file = file
            elif "Q4_K_M" in file and "mmproj" in file:
                log(f"Found mmproj file: {file}")
                mmproj_target_file = file
            #if NO Q4_K_M version, get whatever is available
            elif not "mmproj" in file and "gguf" in file and not model_target_file:
                log(f"Found model file: {file}")
                model_target_file = file
            elif "mmproj" in file and not mmproj_target_file and f"{model_target_file[:-5]}" in file and not mmproj_target_file:
                log(f"Found mmproj file: {file}")
                mmproj_target_file = file
    
        if model_target_file == None:
            fatal(f"Couldn't find requested quantization model in {args.pull_model} repo")

        log(f"Model file: {model_target_file}, mmproj: {mmproj_target_file or ''}")
        log(f"Downloading file: {model_target_file}")
        model_file_path = hf_hub_download(
            repo_id=args.pull_model,
            filename=model_target_file,
        )
        info(f"{model_target_file} Model has succesfully downloaded, file downloaded to: {model_file_path}")

        if mmproj_target_file != None:    
            log(f"Downloading file: {mmproj_target_file}")
            mmproj_file_path = hf_hub_download(
                repo_id=args.pull_model,
                filename=mmproj_target_file,
            )
            info(f"mmproj for model has succesfully downloaded, file downloaded to: {mmproj_file_path}")
        log(f"Creating json entry for model {model_target_file}")
        models_dir_path = Path(f"{GEKOKU_HOME}/models")
        if not models_dir_path.is_dir():
            warn("Models folder doesn't exist at a designated path, creating one")
            models_dir_path.mkdir(parents=True, exist_ok=True)

        model_data = {
            "id": model_target_file[:-5],
            "metadata": {
                "repo": args.pull_model,
                "file": model_target_file,
                "path": model_file_path,
                "mmproj_path": mmproj_file_path or ''
            },
            "arguments": {
                "llama_args": ""
            },
        }
        toml_path = models_dir_path / f"{model_target_file[:-5]}.toml"
        with open(toml_path, "wb") as toml_file:
            tomli_w.dump(model_data, toml_file)
        success("Succesfully pulling from source")
    
    if args.command == "serve":
        info("Starting GekokuAI server...")
        models_dir_path = Path(f"{GEKOKU_HOME}/models")
        for file in models_dir_path.iterdir():
            if file.is_file() and args.serve_model in file.name:
                    log(f"Found model config: {file}")
                    model_toml_path = file
        
        with open(model_toml_path, "rb") as f:
            model_config = tomllib.load(f)
        
        model_path = model_config["metadata"]["path"]
        model_mmproj_path = model_config["metadata"]["mmproj_path"]
        llama_cpp = (Path(config["llama_cpp"]["llama_cpp_path"])/"build"/"bin"/"llama-server")
        llama_args = model_config["arguments"]["llama_args"]
        server_host = config["server"]["host"]
        server_port = config["server"]["port"]
        
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
            cleanup()


    if args.command == "status":
        server_host = config["server"]["host"]
        server_port = config["server"]["port"]
        runtime_dir_path = Path(f"{GEKOKU_HOME}/runtime")
        if not runtime_dir_path.is_dir():
            warn("Runtime folder to store server information doesn't exist, creating one")
            runtime_dir_path.mkdir(parents=True, exist_ok=True)

        runtime_file_path = Path(f"{GEKOKU_HOME}/runtime/runtime.toml")
        if not runtime_file_path.is_file():
            warn("Runtime file not found, creating a default inactive runtime information")
            runtime_data = {
                "server": {
                    "running": False,
                    "pid": 0,
                    "model": "",
                    "host": "",
                    "port": ""
                }
            }
            with open (runtime_file_path, "wb") as toml_file:
                tomli_w.dump(runtime_data, toml_file)
        with open(runtime_file_path, "rb") as f:
            runtime_file = tomllib.load(f)
        status_running = runtime_file["server"]["running"]
        status_pid = runtime_file["server"]["pid"]
        status_model = runtime_file["server"]["model"]
        status_host = runtime_file["server"]["host"]
        status_port = runtime_file["server"]["port"]
        
        print(f"GekokuAI Status:\n\nVersion: {version}\n\nRunning: {status_running}\nPID: {status_pid}\nLoaded model: {status_model}\nHost: {status_host}\nPort: {status_port}")

    if args.command == "stop":
        info("Stopping GekokuAI server...")
        runtime_file_path = Path(f"{GEKOKU_HOME}/runtime/runtime.toml")
        if not runtime_file_path.is_file():
            warn("Runtime file not found, creating a default inactive runtime information")
            runtime_data = {
                "server": {
                    "running": False,
                    "pid": 0,
                    "model": "",
                    "host": "",
                    "port": ""
                }
            }
            with open (runtime_file_path, "wb") as toml_file:
                tomli_w.dump(runtime_data, toml_file)
        with open(runtime_file_path, "rb") as f:
            runtime_file = tomllib.load(f)
        status_pid = runtime_file["server"]["pid"]
        if status_pid != 0:
            os.kill(status_pid, signal.SIGTERM)
            success(f"Server succesfully killed. PID {status_pid}")
        else:
            error("There's no server to stop...")
    
    if args.command == "list":
        print("All downloaded models from huggingface\n\n")
        models_dir_path = Path(f"{GEKOKU_HOME}/models")
        for file in models_dir_path.iterdir():
            model_file_path = models_dir_path / file
            with open(model_file_path, "rb") as f:
                model_info = tomllib.load(f)
            model_id_info = model_info["id"]
            model_repo_info = model_info["metadata"]["repo"]
            model_path_info = model_info["metadata"]["path"]
            print(f"ID: {model_id_info}\nRepository: {model_repo_info}\nFile path: {model_path_info}\n\n")

    if args.command == "remove":
        choice = input(f"Do you really want to remove {args.remove_model} model? (y/n): ")
        if choice in ['y', 'Y', 'yes', 'Yes', 'YES']:
            log(f"Removing {args.remove_model} from shelf...")
            model_info_path = Path(f"{GEKOKU_HOME}/models/{args.remove_model}.toml")
            with open(model_info_path, "rb") as f:
                model_info = tomllib.load(f)
            model_file_path = Path(model_info["metadata"]["path"])
            mmproj_file_path = Path(model_info["metadata"]["mmproj_path"])
            log(f"Removing model file, Path: {model_file_path}")
            model_file_path.unlink(missing_ok=True)
            if mmproj_file_path.name:
                log(f"Removing mmproj file, Path: {mmproj_file_path}")
                mmproj_file_path.unlink(missing_ok=True)
            log(f"Deleting model information...")
            model_info_path.unlink(missing_ok=True)
            success("Model has successfully been removed")
        else:
            info("Removal cancelled...")
            
if __name__ == "__main__":
    main()