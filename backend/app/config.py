from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    app_name: str = Field(default="Orquestrador Rotas LLM")
    debug: bool = Field(default=True)
    secret_key: str = Field(default="change-this-secret", env="SECRET_KEY")
    token_expire_minutes: int = Field(default=60, env="TOKEN_EXPIRE_MINUTES")
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@db:5432/orquestrador",
        env="DATABASE_URL",
    )
    cors_allowed_origins: list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        env="CORS_ALLOWED_ORIGINS",
    )
    gemini_api_key: str | None = Field(default=None, env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", env="GEMINI_MODEL")

    @validator("cors_allowed_origins", pre=True)
    def split_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

