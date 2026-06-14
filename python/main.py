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
# Internal related modules
from utils.vars import GEKOKUAI_VERSION
from utils.logger import *
from utils.toml_manager import *
from utils.daemon_cleanup import *
from modules.doctor import *
from modules.pull_model import *
from modules.serve import *
from modules.status import *
from modules.stop_model import *
from modules.stop_daemon import *
from modules.list_models import *
from modules.remove_model import *
from modules.stop_model import *
from daemon.daemon_start import *

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
    parser_pull.add_argument("--embedding", action="store_true", help="Indicates that the model is an embedding model")
    parser_pull.add_argument("--vision", action="store_true", help="Indicates that the model is a vision model")
    parser_pull.add_argument("--chat-vision", action="store_true", help="Indicates that the model has chat and vision capabilities")

    #serve subcommand
    parser_pull = subparser.add_parser("serve", description="Run llama.cpp backend")
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
    parser_run = subparser.add_parser("load", description="load a downloaded model from huggingface")
    parser_run.add_argument("load_model", help="Which model to load")

    #unload subcommand (TODO)
    # parser_run = subparser.add_parser("unload", description="load a downloaded model from huggingface")
    # parser_run.add_argument("load_model", help="Which model to unload")

    #stop subcommand
    parser_stop = subparser.add_parser("stop", description="Stops the currently running Gekoku Backend")

    args = parser.parse_args()

    if args.command == "info":
        print("GekokuAI\n" + GEKOKUAI_VERSION + "\n")

    if args.command == "doctor":
        start_doctor()

    if args.command == "pull":
        pull_model(args)

    if args.command == "serve":
        start_daemon(args)

    if args.command == "status":
        status(args)

    if args.command == "stop":
        stop_daemon()

    if args.command == "list":
        list_model(args)

    if args.command == "remove":
        remove_model(args)

    if args.command == "load":
        launch_model(args.load_model)
    
    if args.command == "unload":
        stop_model(args)

if __name__ == "__main__":
    main()
