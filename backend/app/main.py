from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path


def _extend_sys_path() -> None:
    deps_root = Path(__file__).resolve().parents[2] / "backend" / ".deps"
    site_packages = list(deps_root.glob("lib/python*/site-packages"))
    for path in site_packages:
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.append(path_str)


_extend_sys_path()

from . import models
from .config import settings
from .database import Base, engine
from .routers import ai, auth, cities



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
    app.include_router(cities.router)
    app.include_router(ai.router)

    @app.get("/api/health", tags=["health"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()

