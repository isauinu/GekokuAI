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
try:
    import tomlib
except ImportError:
    import tomli as tomlib
import tomli_w
import subprocess
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download
import signal
# Internal related modules
from utils.logger import *
from utils.toml_manager import *
from utils.daemon_cleanup import *
from modules.doctor import *
from modules.model_manager import *
from modules.serve import *
from modules.status import *

#Get the location where $HOME is located
HOME = os.getenv('HOME')
config = read_toml(f"{HOME}/.gekokuai/config/config.toml") #GekokuAI default config
GEKOKU_HOME = config["location"]["workspace"]

signal.signal(signal.SIGTERM, daemon_cleanup)

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
        start_doctor()

    if args.command == "pull":
        pull_model(args)
    
    if args.command == "serve":
        serve_model(args)


    if args.command == "status":
        status(args)

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
            runtime_file = tomlib.load(f)
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
                model_info = tomlib.load(f)
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
                model_info = tomlib.load(f)
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