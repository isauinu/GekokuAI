from fastapi import APIRouter, HTTPException, status
from utils.logger import *
from utils.vars import API_PREFIX
from pydantic import BaseModel
from modules.serve import *

class LoadRequest(BaseModel):
    model: str

router = APIRouter(prefix=API_PREFIX)

@router.post("/load")
def load(req: LoadRequest):
    response = launch_model(req.model)
    if response:
        return {
            "response": response,
            "model": req.model
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to find model with that name or the existing model has already been started"
        )
