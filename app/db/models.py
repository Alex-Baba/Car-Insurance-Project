from app.db.base import datab as db
from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, field_validator, ValidationError, Field, ConfigDict

YEAR_MIN = 1900
YEAR_MAX = 2100

def _check_range(d: date):
    if d.year < YEAR_MIN or d.year > YEAR_MAX:
        raise ValueError(f"Date year must be between {YEAR_MIN} and {YEAR_MAX}")
    return d

class PolicyCreate(BaseModel):
    model_config = ConfigDict(strict=True, populate_by_name=True)
    provider: str
    startDate: date = Field(alias="start_date")
    endDate: date = Field(alias="end_date")
    carId: int = Field(alias="car_id")

    @field_validator("startDate", "endDate")
    def range_ok(cls, v: date):
        return _check_range(v)

    @field_validator("endDate")
    def order_ok(cls, v: date, info):
        start = info.data.get("startDate")
        if start and v < start:
            raise ValueError("endDate must be >= startDate")
        return v

class PolicyUpdate(BaseModel):
    model_config = ConfigDict(strict=True, populate_by_name=True)
    provider: str | None = None
    startDate: date | None = Field(default=None, alias="start_date")
    endDate: date | None = Field(default=None, alias="end_date")

    @field_validator("startDate", "endDate")
    def range_ok(cls, v: date | None):
        return _check_range(v) if v else v

    @field_validator("endDate")
    def order_ok(cls, v: date | None, info):
        start = info.data.get("startDate")
        if v and start and v < start:
            raise ValueError("endDate must be >= startDate")
        return v

class ClaimCreate(BaseModel):
    model_config = ConfigDict(strict=True)
    claimDate: date
    description: str
    amount: Decimal
    carId: int

    @field_validator("claimDate")
    def validate_claim_date(cls, v: date):
        v = _check_range(v)
        return v

    @field_validator("description")
    def validate_desc(cls, v: str):
        if not v.strip():
            raise ValueError("description must be non-empty")
        return v

    @field_validator("amount")
    def validate_amount(cls, v: Decimal):
        if v <= 0:
            raise ValueError("amount must be > 0")
        return v

class InsuranceValidityQuery(BaseModel):
    model_config = ConfigDict(strict=True)
    carId: int
    date: date

    @field_validator("date")
    def validate_query_date(cls, v: date):
        return _check_range(v)

class Owner(db.Model):
    __tablename__ = 'owner'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=True)
    
    cars = db.relationship('Car', back_populates='owner', lazy=True, cascade="all, delete-orphan")

class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(), unique=True, nullable=False)
    make = db.Column(db.String(), nullable=True)
    model = db.Column(db.String(), nullable=True)
    year_of_manufacture = db.Column(db.Integer, nullable=True)

    owner_id = db.Column(db.Integer(), db.ForeignKey('owner.id'), nullable=False)
    owner = db.relationship('Owner', back_populates='cars', lazy=True)
    
    insurance_policies = db.relationship('InsurancePolicy', back_populates='car', lazy=True, cascade="all, delete-orphan")  

    claims = db.relationship('Claims', back_populates='car', lazy=True, cascade="all, delete-orphan")

class InsurancePolicy(db.Model):
    __tablename__ = 'insurance_policies'

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(), nullable=False)
    start_date = db.Column(db.Date(), nullable=True)
    end_date = db.Column(db.Date(), nullable=True)

    car_id = db.Column(db.Integer(), db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car', back_populates='insurance_policies', lazy='selectin')

class Claims(db.Model):
    __tablename__ = 'claims'

    id = db.Column(db.Integer, primary_key=True)
    claim_date = db.Column(db.Date(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now(), nullable=False)

    car_id = db.Column(db.Integer(), db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car', lazy='selectin')