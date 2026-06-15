from fastapi import APIRouter, HTTPException, status
from utils.toml_manager import *
from utils.vars import API_PREFIX, RUNTIME_DAEMON_DATA, MODELS_DIR_PATH
from fastapi import Request
from utils.logger import *
import requests
from pathlib import Path

router = APIRouter(prefix=API_PREFIX)

@router.post("/embeddings")
async def chat(req: Request):
    info("Proxying data to the appropiate endpoint and port")
    body = await req.json()
    log(f"type of request: {type(body)}")
    log(f"Content of request: {body}")
    models_list = RUNTIME_DAEMON_DATA["server"]["models"]
    model = body["model"]
    if not model in models_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to find model with that name"
        )
    log(f"Found model: {model}")
    port = RUNTIME_DAEMON_DATA[model]["port"]
    log(f"Found port for targeted model at: {port}")
    
    response = requests.post(f"http://localhost:{port}/v1/embeddings", json=body)
    log(f"Response Text: {response.text}")
    log(f"Status Code: {response.status_code}")

    model_file_path = Path(MODELS_DIR_PATH, f"{model}.toml")
    model_info = read_toml(model_file_path)
    if not model_info["capabilities"]["embedding"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model does not support embedding"
        )
    return response.json()