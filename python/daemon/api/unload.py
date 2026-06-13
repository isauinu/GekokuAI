from fastapi import APIRouter
from utils.logger import *
from utils.vars import API_PREFIX
from pydantic import BaseModel
from modules.stop_model import *

class LoadRequest(BaseModel):
    model: str

router = APIRouter(prefix=API_PREFIX)

@router.post("/unload")
def load(req: LoadRequest):
    stop_model(req.model)
    return {
        "received": req.model
    }