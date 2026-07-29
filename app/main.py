# registering routes and main entry point of project 
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers.document import router as document_router
from app.routers.auth import router as auth_router
from app.routers.ai import router as ai_router
from app.utils.ai import initialize_rag_pipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.rag = initialize_rag_pipeline()
    yield

app = FastAPI(title="UDP AI SaaS", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(document_router)
app.include_router(ai_router)