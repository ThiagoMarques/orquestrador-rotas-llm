from fastapi import FastAPI

from . import models
from .database import Base, engine
from .routers import auth


def create_app() -> FastAPI:
    app = FastAPI(title="Orquestrador Rotas LLM")

    Base.metadata.create_all(bind=engine)

    app.include_router(auth.router)

    @app.get("/api/health", tags=["health"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()

