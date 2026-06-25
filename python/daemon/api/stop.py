from fastapi import APIRouter, Depends
from utils.logger import *
from utils.vars import API_PREFIX
from modules.stop_daemon import *
from utils.check_allowed_ips_api import * 

router = APIRouter(prefix=API_PREFIX)

@router.get("/stop", dependencies=[Depends(check_allowed_hosts)])
def load():
    stop_daemon()
    return {
        "success": "Daemon has been stopped"
    }