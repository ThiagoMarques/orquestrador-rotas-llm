from datetime import date
import json
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user
from ..services.gemini import get_gemini_service


router = APIRouter(prefix="/api/ai", tags=["ai"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    response: str
    routes: list[schemas.RoutePlanRead]


ROUTE_FIELDS = [
    "distance_km",
    "travel_time",
    "cost_brl",
    "trip_type",
    "transport_type",
    "lodging",
    "food",
    "activity",
    "estimated_spend_brl",
]


def _clean_json_payload(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned)
        cleaned = cleaned.rstrip('`').strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Resposta inválida do Gemini.") from exc


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None

    normalized = value.strip().split('T')[0]
    try:
        return date.fromisoformat(normalized)
    except ValueError:
        return None


def _build_csv_row(route: dict[str, Any]) -> str:
    values = [route.get("itinerary", "")] + [
        str(route.get(field) or "").replace(';', ',') for field in ROUTE_FIELDS
    ]
    return ";".join(values)


def _build_prompt(message: str, city_names: list[str]) -> str:
    cities_block = ", ".join(city_names)
    return (
        "Você atua como um planejador de rotas turísticas.\n"
        "Considere apenas as seguintes cidades cadastradas pelo usuário: "
        f"{cities_block}.\n"
        "Com base no pedido abaixo, elabore até 3 rotas que façam sentido apenas"
        " com essas cidades.\n"
        f"Pedido do usuário: \"{message}\".\n"
        "Retorne estritamente um JSON com as chaves 'message' e 'routes'.\n"
        "A chave 'message' deve conter um texto introdutório curto.\n"
        "A chave 'routes' deve ser uma lista em que cada item contém os campos:\n"
        "- itinerary: string no formato 'Cidade A → Cidade B'.\n"
        "- travel_date: data no formato YYYY-MM-DD (escolha uma data coerente; caso não haja indicação, use uma data dentro dos próximos 30 dias).\n"
        "- distance_km, travel_time, cost_brl, trip_type, transport_type, lodging, food, activity, estimated_spend_brl.\n"
        "- summary: duas frases descrevendo a rota.\n"
        "Não escreva nada fora do JSON."
    )


@router.post("/chat", response_model=ChatResponse)
def chat_with_gemini(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cities = (
        db.query(models.City)
        .filter(models.City.user_id == current_user.id)
        .order_by(models.City.created_at.asc())
        .all()
    )

    if not cities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cadastre pelo menos uma cidade antes de solicitar uma rota.",
        )

    city_labels = [f"{city.name}-{city.state}" for city in cities]

    prompt = _build_prompt(payload.message, city_labels)

    try:
        gemini = get_gemini_service()
        raw_text = gemini.generate_text(prompt)
        parsed = _clean_json_payload(raw_text)
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        )

    routes_payload = []
    routes_data = parsed.get("routes") or []
    if not routes_data:
        return ChatResponse(response=parsed.get("message", raw_text), routes=[])

    created_routes: list[models.RoutePlan] = []

    for route in routes_data:
        itinerary = route.get("itinerary")
        if not itinerary:
            continue

        model = models.RoutePlan(
            user_id=current_user.id,
            itinerary=itinerary,
            travel_date=_parse_date(route.get("travel_date")),
            distance_km=route.get("distance_km"),
            travel_time=route.get("travel_time"),
            cost_brl=route.get("cost_brl"),
            trip_type=route.get("trip_type"),
            transport_type=route.get("transport_type"),
            lodging=route.get("lodging"),
            food=route.get("food"),
            activity=route.get("activity"),
            estimated_spend_brl=route.get("estimated_spend_brl"),
            summary=route.get("summary"),
            csv_row=_build_csv_row(route),
        )

        db.add(model)
        created_routes.append(model)

    db.commit()

    for model in created_routes:
        db.refresh(model)
        routes_payload.append(schemas.RoutePlanRead.from_orm(model))

    message = parsed.get("message") or "Planejamento gerado com sucesso."

    return ChatResponse(response=message, routes=routes_payload)

