from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from utils.logger import *
from utils.globals import API_PREFIX
from pydantic import BaseModel
from modules.serve import *

class LoadRequest(BaseModel):
    model: str

router = APIRouter(prefix=API_PREFIX)

@router.post("/load")
def load(req: LoadRequest):
    response = launch_model(req.model)
    is_success = response.pop("result", None) 
    if is_success:
        response = {"status": "Success", **response}
        return response
    else:
        response = {"status": "Failed", **response}
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=response
        )