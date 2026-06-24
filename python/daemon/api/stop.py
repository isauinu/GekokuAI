from fastapi import APIRouter
from utils.logger import *
from utils.vars import API_PREFIX
from modules.stop_daemon import *
from utils.check_allowed_ips_api import * 

router = APIRouter(prefix=API_PREFIX)

@router.get("/stop")
def load():
    check_allowed_hosts()
    stop_daemon()
    return {
        "success": "Daemon has been stopped"
    }