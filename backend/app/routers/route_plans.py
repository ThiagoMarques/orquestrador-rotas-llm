from datetime import date
from io import StringIO

import csv
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user


router = APIRouter(prefix="/api/routes", tags=["routes"])


@router.get("/", response_model=list[schemas.RoutePlanRead])
def list_routes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    routes = (
        db.query(models.RoutePlan)
        .filter(models.RoutePlan.user_id == current_user.id)
        .order_by(models.RoutePlan.created_at.desc())
        .all()
    )
    return routes


@router.get("/{route_id}", response_model=schemas.RoutePlanDetail)
def get_route_detail(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    route = (
        db.query(models.RoutePlan)
        .filter(models.RoutePlan.id == route_id, models.RoutePlan.user_id == current_user.id)
        .first()
    )
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rota não encontrada.")

    return route


@router.get("/{route_id}/csv")
def download_route_csv(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    route = (
        db.query(models.RoutePlan)
        .filter(models.RoutePlan.id == route_id, models.RoutePlan.user_id == current_user.id)
        .first()
    )
    if not route or not route.csv_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado.")

    headers = [
        "Percurso",
        "Distância",
        "Tempo de viagem",
        "Custo da viagem",
        "Tipo de viagem",
        "Tipo de transporte",
        "Tipo de hospedagem",
        "Tipo de alimentação",
        "Tipo de atividade",
        "Gasto estimado",
    ]

    output = StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(headers)
    writer.writerow(route.csv_row.split(';'))
    output.seek(0)

    filename = f"rota-{route_id}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

