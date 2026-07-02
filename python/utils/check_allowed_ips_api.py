from fastapi import Request, HTTPException, status
from utils.globals import CONFIG_DATA

def check_allowed_hosts(request: Request):
    if CONFIG_DATA["security"]["host_managed_endpoints"]:
        allowed_hosts = CONFIG_DATA["security"]["allowed_hosts"]
        if request.client.host not in allowed_hosts:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Forbidden"
            )