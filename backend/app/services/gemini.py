from functools import lru_cache
from typing import Optional

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

from ..config import settings


class GeminiService:
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurado.")

        genai.configure(api_key=api_key)
        self._model_name = model

    def generate_text(self, prompt: str) -> str:
        if not prompt:
            raise ValueError("O prompt não pode ser vazio.")

        try:
            model = genai.GenerativeModel(self._model_name)
            result = model.generate_content(prompt)
        except GoogleAPIError as exc:  # erros da API do Google
            raise RuntimeError(f"Erro ao conectar ao Gemini: {exc}") from exc
        except Exception as exc:  # fallback genérico
            raise RuntimeError("Falha ao processar a resposta do Gemini.") from exc

        text: Optional[str] = getattr(result, "text", None)
        if not text:
            raise RuntimeError("Resposta vazia do Gemini.")

        return text.strip()


@lru_cache(maxsize=1)
def get_gemini_service() -> GeminiService:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY não configurado no backend.")

    return GeminiService(api_key=settings.gemini_api_key, model=settings.gemini_model)

