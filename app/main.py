# registering routes and main entry point of project 
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.documents.router import router as document_router
from app.auth.router import router as auth_router
from app.db.base import Base
from app.db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

app = FastAPI(title="UDP AI SaaS", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(document_router)
