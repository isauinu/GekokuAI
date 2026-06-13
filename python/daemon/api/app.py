from fastapi import FastAPI

from api.status import router as status_router
from api.load import router as load_router
from api.unload import router as unload_router
from api.stop import router as stop_router

app = FastAPI()

app.include_router(status_router)
app.include_router(load_router)
app.include_router(unload_router)
app.include_router(stop_router)