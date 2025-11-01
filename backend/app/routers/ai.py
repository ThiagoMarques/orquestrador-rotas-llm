from datetime import date
import json
import re
from typing import Any, Iterable

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


def _group_cities(cities: Iterable[models.City]) -> tuple[models.City | None, models.City | None, list[models.City]]:
    origin = None
    destination = None
    intermediates: list[models.City] = []

    for city in cities:
        role = getattr(city, "role", None) or "intermediate"
        if role == "origin" and origin is None:
            origin = city
        elif role == "destination" and destination is None:
            destination = city
        else:
            intermediates.append(city)

    return origin, destination, intermediates


def _format_city(city: models.City | None) -> str:
    if not city:
        return "Não definida"
    return f"{city.name}-{city.state}"


def _format_intermediates(intermediates: list[models.City]) -> str:
    if not intermediates:
        return "Nenhuma"
    return ", ".join(f"{city.name}-{city.state}" for city in intermediates)


def _format_routes_block(route_plans: list[models.RoutePlan]) -> str:
    if not route_plans:
        return "Nenhuma rota planejada previamente."

    lines: list[str] = []
    for index, plan in enumerate(route_plans, start=1):
        parts = [
            f"Itinerário: {plan.itinerary}",
            f"Data: {plan.travel_date.isoformat() if plan.travel_date else 'indefinida'}",
        ]

        if plan.distance_km:
            parts.append(f"Distância: {plan.distance_km}")
        if plan.travel_time:
            parts.append(f"Tempo: {plan.travel_time}")
        if plan.transport_type:
            parts.append(f"Transporte: {plan.transport_type}")
        if plan.summary:
            parts.append(f"Resumo: {plan.summary}")

        lines.append(f"{index}. " + "; ".join(parts))

    return "\n".join(lines)


def _build_prompt(
    message: str,
    origin: models.City,
    destination: models.City,
    intermediates: list[models.City],
    existing_routes: list[models.RoutePlan],
) -> str:
    origin_block = _format_city(origin)
    destination_block = _format_city(destination)
    intermediate_block = _format_intermediates(intermediates)
    planned_routes_block = _format_routes_block(existing_routes)

    return (
        "Você atua como um planejador de rotas turísticas.\n"
        f"Cidade de origem definida pelo usuário: {origin_block}.\n"
        f"Cidade de destino definida pelo usuário: {destination_block}.\n"
        f"Cidades intermediárias cadastradas: {intermediate_block}.\n"
        "Histórico de rotas planejadas anteriormente (mais recentes primeiro):\n"
        f"{planned_routes_block}\n"
        "Analise esse histórico e utilize-o como referência para responder ao novo pedido.\n"
        f"Pedido atual do usuário: \"{message}\".\n"
        "Retorne estritamente um JSON com as chaves 'message' e 'routes'.\n"
        "A chave 'message' deve conter um texto curto justificando a escolha da melhor rota entre as opções possíveis.\n"
        "A chave 'routes' deve ser uma lista com apenas um item contendo os campos:\n"
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

    origin, destination, intermediates = _group_cities(cities)

    if not origin or not destination:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Defina cidades de origem e destino antes de solicitar uma rota.",
        )

    existing_routes = (
        db.query(models.RoutePlan)
        .filter(models.RoutePlan.user_id == current_user.id)
        .order_by(models.RoutePlan.created_at.desc())
        .limit(10)
        .all()
    )

    prompt = _build_prompt(payload.message, origin, destination, intermediates, existing_routes)

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

        parsed_travel_date = _parse_date(route.get("travel_date"))
        if not parsed_travel_date or parsed_travel_date < date.today():
            parsed_travel_date = date.today()

        model = models.RoutePlan(
            user_id=current_user.id,
            itinerary=itinerary,
            travel_date=parsed_travel_date,
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

