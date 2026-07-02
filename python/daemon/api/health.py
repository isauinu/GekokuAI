from fastapi import APIRouter
from utils.globals import API_PREFIX

router = APIRouter(prefix=API_PREFIX)

@router.get("/health")
def check_health():
    return {"status": "ok"}