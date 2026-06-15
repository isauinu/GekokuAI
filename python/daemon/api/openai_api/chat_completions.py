from fastapi import APIRouter, HTTPException ,status
from utils.toml_manager import *
from utils.vars import API_PREFIX, RUNTIME_DAEMON_DATA
from fastapi import Request
from utils.logger import *
import requests
from fastapi.responses import StreamingResponse

router = APIRouter(prefix=API_PREFIX)

@router.post("/chat/completions")
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
    if body.get("stream") == False:
        response = requests.post(f"http://localhost:{port}/v1/chat/completions", json=body)
        log(f"Response Text: {response.text}")
        log(f"Status Code: {response.status_code}")
        return response.json()
    elif body.get("stream") == True:
        response = requests.post(f"http://localhost:{port}/v1/chat/completions", json=body, stream=True)
        log(response.headers.get("content-type"))
        def generate():
            for line in response.iter_lines():
                if line:
                    yield line + b"\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request"
        )