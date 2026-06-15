from fastapi import Request

# (TODO)
# Used to check if an endpoint is accessed through localhost only: notable endpoints: load unload stop
def check_allowed_ip():
    return