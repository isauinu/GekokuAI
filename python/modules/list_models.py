from pathlib import Path
from utils.globals import MODELS_DIR_PATH
from utils.toml_manager import *

def list_model(args):
    print("All downloaded models from huggingface\n\n")
    for file in MODELS_DIR_PATH.iterdir():
        model_file_path = Path(MODELS_DIR_PATH, file)
        model_info = read_toml(model_file_path)
        model_id_info = model_info["id"]
        model_repo_info = model_info["metadata"]["repo"]
        model_path_info = model_info["metadata"]["path"]
        print(f"ID: {model_id_info}\nRepository: {model_repo_info}\nFile path: {model_path_info}\n\n")