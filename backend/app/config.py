from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field(default="Orquestrador Rotas LLM")
    debug: bool = Field(default=True)
    secret_key: str = Field(default="change-this-secret", env="SECRET_KEY")
    token_expire_minutes: int = Field(default=60, env="TOKEN_EXPIRE_MINUTES")
    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@db:5432/orquestrador",
        env="DATABASE_URL",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

