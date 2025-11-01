from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
ROLE_LABELS = {
    "origin": "origem",
    "destination": "destino",
}


def _ensure_role_constraints(db: Session, user_id: int, role: str, *, exclude_id: int | None = None) -> None:
    if role not in ROLE_LABELS:
        return

    query = (
        db.query(models.City)
        .filter(models.City.user_id == user_id, models.City.role == role)
    )

    if exclude_id is not None:
        query = query.filter(models.City.id != exclude_id)

    exists = query.first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma cidade marcada como {ROLE_LABELS[role]}.",
        )

from ..database import get_db
from ..dependencies import get_current_user


router = APIRouter(prefix="/api/cities", tags=["cities"])


@router.get("/", response_model=list[schemas.CityRead])
def list_cities(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cities = (
        db.query(models.City)
        .filter(models.City.user_id == current_user.id)
        .order_by(models.City.created_at.desc())
        .all()
    )
    return cities


@router.post("/", response_model=schemas.CityRead, status_code=status.HTTP_201_CREATED)
def create_city(
    city_in: schemas.CityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    normalized_name = city_in.name.strip()
    normalized_state = city_in.state.strip().upper()

    existing = (
        db.query(models.City)
        .filter(
            models.City.user_id == current_user.id,
            models.City.name == normalized_name,
            models.City.state == normalized_state,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cidade já cadastrada para este usuário.",
        )

    _ensure_role_constraints(db, current_user.id, city_in.role)

    city = models.City(
        name=normalized_name,
        state=normalized_state,
        role=city_in.role,
        user_id=current_user.id,
    )
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


@router.put("/{city_id}", response_model=schemas.CityRead)
def update_city(
    city_id: int,
    city_in: schemas.CityUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    city = (
        db.query(models.City)
        .filter(models.City.id == city_id, models.City.user_id == current_user.id)
        .first()
    )
    if not city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cidade não encontrada.")

    new_name = city_in.name.strip() if city_in.name is not None else city.name
    new_state = city_in.state.strip().upper() if city_in.state is not None else city.state

    duplicate = (
        db.query(models.City)
        .filter(
            models.City.user_id == current_user.id,
            models.City.id != city.id,
            models.City.name == new_name,
            models.City.state == new_state,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma cidade cadastrada com este nome e UF.",
        )

    if city_in.name is not None:
        city.name = new_name
    if city_in.state is not None:
        city.state = new_state
    if city_in.role is not None:
        _ensure_role_constraints(db, current_user.id, city_in.role, exclude_id=city.id)
        city.role = city_in.role

    db.commit()
    db.refresh(city)
    return city


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_city(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    city = (
        db.query(models.City)
        .filter(models.City.id == city_id, models.City.user_id == current_user.id)
        .first()
    )
    if not city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cidade não encontrada.")

    db.delete(city)
    db.commit()

