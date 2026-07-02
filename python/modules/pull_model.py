from huggingface_hub import HfApi, hf_hub_download, utils
from pathlib import Path
from utils.logger import *
from utils.toml_manager import *
from utils.globals import MODELS_DIR_PATH
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
    model_capabilities = []

    if args.vision:
        log("Model is determined to have vision capability")
    elif args.embedding:
        log("Model is determined to be embedding model")
        model_capabilities.append("embedding")
    elif args.reranking:
        log("Model is determined to be a reranking model")
        model_capabilities.append("reranking")

    log(f"Found the following files in {args.pull_model}:")
    #Get model file
    for file in files:
        verbose(file)
        #Get model when quantization is specified
        if args.quantization:
            if args.quantization in file or args.quantization.lower() in file or args.quantization.casefold() in file and not "mmproj" in file:
                verbose(f"Found model file: {file}")
                model_target_file = file
            if args.quantization in file or args.quantization.lower() in file or args.quantization.casefold() in file and "mmproj" in file:
                verbose(f"Found mmproj file: {file}")
                mmproj_target_file = file
                model_capabilities.append("vision")
            if args.vision and "mmproj" in file:
                verbose(f"Found mmproj file: {file}")
                mmproj_target_file = file
                model_capabilities.append("vision")
        else:
            #if no quantization specified, Get Q4_K_M by default
            if "Q4_K_M" in file or "Q4_K_M".lower() in file or "Q4_K_M".casefold() in file:
                if not "mmproj" in file:
                    verbose(f"Found model file: {file}")
                    model_target_file = file
                if "mmproj" in file:
                    verbose(f"Found mmproj file: {file}")
                    mmproj_target_file = file
                    model_capabilities.append("vision")
                if args.vision and "mmproj" in file:
                    verbose(f"Found mmproj file: {file}")
                    mmproj_target_file = file
                    model_capabilities.append("vision")
            else:
                #if NO Q4_K_M version, get whatever is available
                if not "mmproj" in file and "gguf" in file and not model_target_file:
                    verbose(f"Found model file: {file}")
                    model_target_file = file
                if "mmproj" in file and not mmproj_target_file and f"{model_target_file[:-5]}" in file:
                    verbose(f"Found mmproj file: {file}")
                    mmproj_target_file = file
                    model_capabilities.append("vision")
                if args.vision and "mmproj" in file and not mmproj_target_file:
                    verbose(f"Found mmproj file: {file}")
                    mmproj_target_file = file
                    model_capabilities.append("vision")

    if model_target_file == None:
        fatal(f"Couldn't find requested quantization model in {args.pull_model} repo")

    log(f"Model file: {model_target_file}, mmproj: {mmproj_target_file or ''}")
    verbose(f"Capabilities: is_vision: {"vision" in model_capabilities}, is_embedding: {"embedding" in model_capabilities}, is_reranking: {"reranking" in model_capabilities}")
    if args.vision and not mmproj_target_file:
        error("No mmproj is found on the repo, resuming installation without it")
    
    log(f"Downloading file: {model_target_file}")
    model_file_path = hf_hub_download(
        repo_id=args.pull_model,
        filename=model_target_file,
    )
    verbose(f"Model path located at {model_file_path}")
    info(f"{model_target_file} Model has succesfully downloaded")

    if mmproj_target_file != None:    
        log(f"Downloading file: {mmproj_target_file}")
        mmproj_file_path = hf_hub_download(
            repo_id=args.pull_model,
            filename=mmproj_target_file,
        )
        verbose(f"{model_target_file} mmproj path located at {model_file_path}")
        info(f"{mmproj_target_file} has succesfully downloaded")
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
            "created": int(time.time()),
            "capabilities": model_capabilities
        },
        "arguments": {
            "llama_args": ""
        },
    }
    verbose(f"Model data content: {model_data}")
    
    toml_path = Path(f"{MODELS_DIR_PATH}", f"{model_target_file[:-5]}.toml")
    write_toml(toml_path, model_data)
    success("Succesfully pulling from source")