from fastapi import APIRouter
from utils.vars import API_PREFIX, MODELS_DIR_PATH
from pathlib import Path
from utils.toml_manager import *

router = APIRouter(prefix=API_PREFIX)

@router.get("/models")
def get_models():
    models = []
    for file in MODELS_DIR_PATH.iterdir():
        model_file_path = Path(MODELS_DIR_PATH, file)
        model_info = read_toml(model_file_path)
        models.append({
            "id": model_info["id"],
            "object": "model",
            "repo": model_info["metadata"]["repo"],
            "file": model_info["metadata"]["file"],
            "created": model_info["metadata"]["created"],
            "owned_by": "gekokuai"
        })
    return {
        "object": "list",
        "data": models
    }

@router.get("/models/{model_id}")
def get_model_info(model_id: str):
    models = []
    model_file_path = Path(MODELS_DIR_PATH, f"{model_id}.toml")
    model_info = read_toml(model_file_path)
    models.append({
            "id": model_info["id"],
            "object": "model",
            "repo": model_info["metadata"]["repo"],
            "file": model_info["metadata"]["file"],
            "created": model_info["metadata"]["created"],
            "owned_by": "gekokuai"
        })
    return {
        "object": "list",
        "data": models
    }
