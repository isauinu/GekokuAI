from huggingface_hub import HfApi, hf_hub_download, utils
from pathlib import Path
from utils.logger import *
from utils.toml_manager import *
from utils.vars import MODELS_DIR_PATH
import time
from utils.interrupt_handler import *

def pull_model(args):
    info("Starting model pull from hugging face")
    api = HfApi()
    try:
        files = api.list_repo_files(repo_id=f"{args.pull_model}")
    except utils.RepositoryNotFoundError:
        error(f"No model found with the repo name {args.pull_model}")
        fatal("Aborting...")
    except Exception as e:
        error(f"An unknown error occured: {e}")
        fatal("Aborting...")
    
    model_target_file = None
    mmproj_target_file = None
    capability_chat = True
    capability_vision = False
    capability_embedding = False

    if args.vision:
        log("Model is determined to have vision capability")
    elif args.embedding:
        log("Model is determined to be embedding model")
        capability_chat = False
        capability_vision = False
        capability_embedding = True

    log(f"Found the following files in {args.pull_model}:")
    #Get model file
    for file in files:
        print(file, end=", ")
        #Get model when quantization is specified
        if args.quantization:
            if args.quantization in file or args.quantization.lower() in file or args.quantization.casefold() in file and not "mmproj" in file:
                log(f"Found model file: {file}")
                model_target_file = file
            if args.quantization in file or args.quantization.lower() in file or args.quantization.casefold() in file and "mmproj" in file:
                log(f"Found mmproj file: {file}")
                mmproj_target_file = file
                capability_chat = True
                capability_vision = True
            if args.vision and "mmproj" in file:
                log(f"Found mmproj file: {file}")
                mmproj_target_file = file
                capability_chat = True
                capability_vision = True
        else:
            #if no quantization specified, Get Q4_K_M by default
            if "Q4_K_M" in file or "Q4_K_M".lower() in file or "Q4_K_M".casefold() in file:
                if not "mmproj" in file:
                    log(f"Found model file: {file}")
                    model_target_file = file
                if "mmproj" in file:
                    log(f"Found mmproj file: {file}")
                    mmproj_target_file = file
                    capability_chat = True
                    capability_vision = True
                if args.vision and "mmproj" in file:
                    log(f"Found mmproj file: {file}")
                    mmproj_target_file = file
                    capability_chat = True
                    capability_vision = True
            else:
                #if NO Q4_K_M version, get whatever is available
                if not "mmproj" in file and "gguf" in file and not model_target_file:
                    log(f"Found model file: {file}")
                    model_target_file = file
                if "mmproj" in file and not mmproj_target_file and f"{model_target_file[:-5]}" in file:
                    log(f"Found mmproj file: {file}")
                    mmproj_target_file = file
                    capability_chat = True
                    capability_vision = True
                if args.vision and "mmproj" in file and not mmproj_target_file:
                    log(f"Found mmproj file: {file}")
                    mmproj_target_file = file
                    capability_chat = True
                    capability_vision = True

    if model_target_file == None:
        fatal(f"Couldn't find requested quantization model in {args.pull_model} repo")

    log(f"Model file: {model_target_file}, mmproj: {mmproj_target_file or ''}")
    log(f"Capabilities: is_chat: {capability_chat}, is_vision: {capability_vision}, is_embedding: {capability_embedding}")
    if args.vision and not mmproj_target_file:
        error("No mmproj is found on the repo, resuming installation without it")
    
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
    else:
        mmproj_file_path = ""
    log(f"Creating json entry for model {model_target_file}")
    
    if not MODELS_DIR_PATH.is_dir():
        warn("Models folder doesn't exist at a designated path, creating one")
        MODELS_DIR_PATH.mkdir(parents=True, exist_ok=True)

    model_data = {
        "id": model_target_file[:-5],
        "metadata": {
            "repo": args.pull_model,
            "file": model_target_file,
            "path": model_file_path,
            "mmproj_path": mmproj_file_path or '',
            "created": int(time.time())
        },
        "arguments": {
            "llama_args": ""
        },
        "capabilities": {
            "chat": capability_chat,
            "vision": capability_vision,
            "embedding": capability_embedding
        }
    }
    
    toml_path = Path(f"{MODELS_DIR_PATH}", f"{model_target_file[:-5]}.toml")
    write_toml(toml_path, model_data)
    success("Succesfully pulling from source")