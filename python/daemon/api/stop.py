from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from utils.logger import *
from utils.globals import API_PREFIX
from modules.stop_daemon import *
from utils.check_allowed_ips_api import * 

router = APIRouter(prefix=API_PREFIX)

@router.get("/stop", dependencies=[Depends(check_allowed_hosts)])
def load():
    response = stop_daemon()
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