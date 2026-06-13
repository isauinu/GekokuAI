from fastapi import APIRouter
from utils.logger import *
from utils.vars import API_PREFIX
from pydantic import BaseModel
from modules.serve import *

class LoadRequest(BaseModel):
    model: str

router = APIRouter(prefix=API_PREFIX)

@router.post("/load")
def load(req: LoadRequest):
    launch_model(req.model)
    return {
        "received": req.model
    }