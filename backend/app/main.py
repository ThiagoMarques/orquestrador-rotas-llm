from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
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
from .routers import ai, auth, cities, route_plans



def _ensure_city_role_column() -> None:
    with engine.connect() as connection:
        connection.execute(text("ALTER TABLE IF EXISTS cities ADD COLUMN IF NOT EXISTS role VARCHAR(20)"))
        connection.execute(text("ALTER TABLE IF EXISTS cities ALTER COLUMN role SET DEFAULT 'intermediate'"))
        connection.execute(text("UPDATE cities SET role = 'intermediate' WHERE role IS NULL"))
        connection.execute(text("ALTER TABLE IF EXISTS cities ALTER COLUMN role SET NOT NULL"))
        constraint_exists = connection.execute(
            text(
                """
                SELECT 1
                FROM information_schema.check_constraints
                WHERE constraint_name = 'ck_city_role'
                LIMIT 1
                """
            )
        ).scalar()
        if not constraint_exists:
            connection.execute(
                text(
                    """
                    ALTER TABLE cities
                    ADD CONSTRAINT ck_city_role
                    CHECK (role IN ('origin','destination','intermediate'))
                    """
                )
            )
        connection.commit()


def create_app() -> FastAPI:
    app = FastAPI(title="Orquestrador Rotas LLM")

    _ensure_city_role_column()
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
    app.include_router(route_plans.router)

    @app.get("/api/health", tags=["health"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()

