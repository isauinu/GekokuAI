from huggingface_hub import HfApi, hf_hub_download
from pathlib import Path
from utils.logger import *
from utils.toml_manager import *
from utils.vars import GEKOKU_HOME

def pull_model(args):
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
        else:
            #if no quantization specified, Get Q4_K_M by default
            if "Q4_K_M" in file:
                if not "mmproj" in file:
                    log(f"Found model file: {file}")
                    model_target_file = file
                if "Q4_K_M" in file and "mmproj" in file:
                    log(f"Found mmproj file: {file}")
                    mmproj_target_file = file
            else:
                #if NO Q4_K_M version, get whatever is available
                if not "mmproj" in file and "gguf" in file and not model_target_file:
                    log(f"Found model file: {file}")
                    model_target_file = file
                if "mmproj" in file and not mmproj_target_file and f"{model_target_file[:-5]}" in file and not mmproj_target_file:
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
    else:
        mmproj_file_path = ""
    log(f"Creating json entry for model {model_target_file}")
    models_dir_path = Path(f"{GEKOKU_HOME}", "models")
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
    toml_path = Path(f"{models_dir_path}", f"{model_target_file[:-5]}.toml")
    write_toml(toml_path, model_data)
    success("Succesfully pulling from source")