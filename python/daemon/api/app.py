from fastapi import FastAPI

from api.status import router as status_router
from api.load import router as load_router
from api.unload import router as unload_router
from api.stop import router as stop_router
from api.health import router as health_router
from api.openai_api.chat_completions import router as oai_chat_completions_router
from api.openai_api.completions import router as oai_completions_router
from api.openai_api.models import router as oai_models_router
from api.openai_api.embeddings import router as oai_embeddings_router
from api.openai_api.responses import router as oai_responses_router
from api.openai_api.rerank import router as rerank_router

app = FastAPI()

app.include_router(status_router)
app.include_router(load_router)
app.include_router(unload_router)
app.include_router(stop_router)
app.include_router(rerank_router)
app.include_router(health_router)

app.include_router(oai_chat_completions_router)
app.include_router(oai_completions_router)
app.include_router(oai_models_router)
app.include_router(oai_embeddings_router)
app.include_router(oai_responses_router)