from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .config import settings
from .database import Base, engine
from .routers import auth


def create_app() -> FastAPI:
    app = FastAPI(title="Orquestrador Rotas LLM")

    Base.metadata.create_all(bind=engine)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)

    @app.get("/api/health", tags=["health"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()

