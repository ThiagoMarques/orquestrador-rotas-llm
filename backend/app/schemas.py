from datetime import date, datetime
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(default=None)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class HomeResponse(BaseModel):
    message: str
    email: EmailStr


class RoutePlanBase(BaseModel):
    itinerary: str
    travel_date: date | None
    distance_km: Optional[str]
    travel_time: Optional[str]
    cost_brl: Optional[str]
    trip_type: Optional[str]
    transport_type: Optional[str]


class RoutePlanRead(RoutePlanBase):
    id: int

    class Config:
        orm_mode = True


class RoutePlanDetail(RoutePlanBase):
    lodging: Optional[str]
    food: Optional[str]
    activity: Optional[str]
    estimated_spend_brl: Optional[str]
    summary: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class RoutePlanBulkDelete(BaseModel):
    route_ids: list[int] = Field(..., min_items=1, description="Lista de IDs de rotas a remover")


CityRole = Literal["origin", "destination", "intermediate"]


class CityBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    state: str = Field(min_length=2, max_length=2)
    role: CityRole = Field(default="intermediate")


class CityCreate(CityBase):
    pass


class CityUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    state: Optional[str] = Field(default=None, min_length=2, max_length=2)
    role: Optional[CityRole] = Field(default=None)


class CityRead(CityBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

