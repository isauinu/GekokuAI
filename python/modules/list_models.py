from pathlib import Path
from utils.globals import MODELS_DIR_PATH
from utils.toml_manager import *

def list_model(args):
    
    models_list = []
    models_repo_list = []
    
    print("All downloaded models\n")
    for file in MODELS_DIR_PATH.iterdir():
        model_file_path = Path(MODELS_DIR_PATH, file)
        model_info = read_toml(model_file_path)
        model_id_info = model_info["id"]
        models_list.append(model_id_info)
        model_repo_info = model_info["metadata"]["repo"]
        models_repo_list.append(model_repo_info)
    
    max_width_model_id = max(len(item) for item in models_list) + 5
    max_width_model_repo = max(len(item) for item in models_repo_list) + 5
    max_width_capability = 20

    print(f"{"Model ID":<{max_width_model_id}}{"Repository":<{max_width_model_repo}}{"Capability":<{max_width_capability}}")
    print(f"{"":-^{max_width_model_id + max_width_model_repo + max_width_capability}}")

    for file in MODELS_DIR_PATH.iterdir():
        model_file_path = Path(MODELS_DIR_PATH, file)
        model_info = read_toml(model_file_path)
        model_id_info = model_info["id"]
        model_repo_info = model_info["metadata"]["repo"]
        model_capability_info = model_info["metadata"]["capabilities"]
        print(f"{model_id_info:<{max_width_model_id}}{model_repo_info:<{max_width_model_repo}}{" ".join(model_capability_info) or "chat":<{max_width_capability}}")