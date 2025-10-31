from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
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
    existing = (
        db.query(models.City)
        .filter(
            models.City.user_id == current_user.id,
            models.City.name == city_in.name,
            models.City.state == city_in.state,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cidade já cadastrada para este usuário.",
        )

    city = models.City(name=city_in.name, state=city_in.state, user_id=current_user.id)
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

    if city_in.name is not None:
        city.name = city_in.name
    if city_in.state is not None:
        city.state = city_in.state

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

