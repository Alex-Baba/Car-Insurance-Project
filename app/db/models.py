from __future__ import annotations
from app.db.base import datab as db
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Date, ForeignKey, Numeric, Text, DateTime, Index

YEAR_MIN = 1900
YEAR_MAX = 2100

def _check_range(d: date):
    if d.year < YEAR_MIN or d.year > YEAR_MAX:
        raise ValueError(f"Date year must be between {YEAR_MIN} and {YEAR_MAX}")
    return d

class Owner(db.Model):
    __tablename__ = "owner"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    cars: Mapped[List["Car"]] = relationship(back_populates="owner")

class Car(db.Model):
    __tablename__ = "car"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vin: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    make: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    year_of_manufacture: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("owner.id"), nullable=False)

    owner: Mapped["Owner"] = relationship(back_populates="cars")
    insurance_policies: Mapped[List["InsurancePolicy"]] = relationship(back_populates="car", cascade="all, delete-orphan")
    claims: Mapped[List["Claim"]] = relationship(back_populates="car", cascade="all, delete-orphan")

class InsurancePolicy(db.Model):
    __tablename__ = "insurance_policy"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("car.id"), nullable=False, index=True)
    provider: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    # Idempotent expiry logging (Task D)
    logged_expiry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    car: Mapped["Car"] = relationship(back_populates="insurance_policies")

    __table_args__ = (
        Index("ix_policy_car_start_end", "car_id", "start_date", "end_date"),
        Index("ix_policy_car_end", "car_id", "end_date"),
    )

class Claim(db.Model):
    __tablename__ = "claim"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("car.id"), nullable=False, index=True)
    claim_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    car: Mapped["Car"] = relationship(back_populates="claims")

    __table_args__ = (
        Index("ix_claim_car_claim_date", "car_id", "claim_date"),
    )