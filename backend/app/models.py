from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cities = relationship(
        "City",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    route_plans = relationship(
        "RoutePlan",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class City(Base):
    __tablename__ = "cities"
    __table_args__ = (
        UniqueConstraint("user_id", "name", "state", name="uq_city_user_name_state"),
        CheckConstraint(
            "role IN ('origin','destination','intermediate')",
            name="ck_city_role",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    state = Column(String(2), nullable=False)
    role = Column(String(20), nullable=False, server_default="intermediate")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="cities")


class RoutePlan(Base):
    __tablename__ = "route_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    itinerary = Column(String(255), nullable=False)
    travel_date = Column(Date, nullable=True)
    distance_km = Column(String(64), nullable=True)
    travel_time = Column(String(64), nullable=True)
    cost_brl = Column(String(64), nullable=True)
    trip_type = Column(String(64), nullable=True)
    transport_type = Column(String(64), nullable=True)
    lodging = Column(String(64), nullable=True)
    food = Column(String(64), nullable=True)
    activity = Column(String(64), nullable=True)
    estimated_spend_brl = Column(String(64), nullable=True)
    summary = Column(String(2048), nullable=True)
    csv_row = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="route_plans")

