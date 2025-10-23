from datetime import date
from pydantic import BaseModel, Field, field_validator, ConfigDict, condecimal

# ---- Pydantic request models (flask-pydantic @validate()) ----
YEAR_MIN = 1900
YEAR_MAX = 2100

def _range(d: date):
    if d.year < YEAR_MIN or d.year > YEAR_MAX:
        raise ValueError(f"Date year must be between {YEAR_MIN} and {YEAR_MAX}")
    return d

class OwnerCreate(BaseModel):
    # relax strict to allow basic JSON coercion
    model_config = ConfigDict(strict=False)
    name: str
    email: str | None = None

class CarCreate(BaseModel):
    model_config = ConfigDict(strict=False, populate_by_name=True)
    vin: str
    make: str
    model: str
    year_of_manufacture: int
    owner_id: int

class CarUpdate(BaseModel):
    model_config = ConfigDict(strict=False, populate_by_name=True)
    vin: str | None = None
    make: str | None = None
    model: str | None = None
    year_of_manufacture: int | None = None

class PolicyCreate(BaseModel):
    model_config = ConfigDict(strict=False, populate_by_name=True)
    provider: str
    startDate: date = Field(alias="start_date")
    endDate: date = Field(alias="end_date")
    carId: int = Field(alias="car_id")

    @field_validator("startDate", "endDate")
    def range_ok(cls, v: date):
        return _range(v)

    @field_validator("endDate")
    def order_ok(cls, v: date, info):
        sd = info.data.get("startDate")
        if sd and v < sd:
            raise ValueError("endDate must be >= startDate")
        return v

class PolicyUpdate(BaseModel):
    model_config = ConfigDict(strict=False, populate_by_name=True)
    provider: str | None = None
    startDate: date | None = Field(default=None, alias="start_date")
    endDate: date | None = Field(default=None, alias="end_date")

    @field_validator("startDate", "endDate")
    def range_opt(cls, v: date | None):
        return _range(v) if v else v

    @field_validator("endDate")
    def order_opt(cls, v: date | None, info):
        sd = info.data.get("startDate")
        if v and sd and v < sd:
            raise ValueError("endDate must be >= startDate")
        return v

class ClaimCreate(BaseModel):
    model_config = ConfigDict(strict=False, populate_by_name=True)
    claimDate: date = Field(alias="claim_date")
    description: str
    amount: condecimal(gt=0)
    carId: int = Field(alias="car_id")

    @field_validator("claimDate")
    def range_claim(cls, v: date):
        return _range(v)

    @field_validator("description")
    def non_empty(cls, v: str):
        if not v.strip():
            raise ValueError("description must be non-empty")
        return v

class InsuranceValidityQuery(BaseModel):
    model_config = ConfigDict(strict=False)
    carId: int
    date: date

    @field_validator("date")
    def range_validity(cls, v: date):
        return _range(v)

# ---- Pydantic output models ----
class PolicyOut(BaseModel):
    id: int
    provider: str | None = None
    startDate: date = Field(alias="start_date")
    endDate: date = Field(alias="end_date")
    carId: int = Field(alias="car_id")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class ClaimOut(BaseModel):
    id: int
    claimDate: date = Field(alias="claim_date")
    description: str
    amount: condecimal(gt=0)
    carId: int = Field(alias="car_id")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

# ---- Additional Pydantic output models (migration targets) ----
class OwnerOut(BaseModel):
    id: int
    name: str
    email: str | None = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class CarOut(BaseModel):
    id: int
    vin: str
    make: str
    model: str
    yearOfManufacture: int = Field(alias="year_of_manufacture")
    ownerId: int = Field(alias="owner_id")
    owner: OwnerOut | None = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class HistoryEntryOut(BaseModel):
    type: str  # POLICY or CLAIM
    policyId: int | None = None
    startDate: str | None = None
    endDate: str | None = None
    provider: str | None = None
    claimId: int | None = None
    claimDate: str | None = None
    amount: condecimal(gt=0) | None = None
    description: str | None = None

    model_config = ConfigDict(populate_by_name=True)

class InsuranceValidityOut(BaseModel):
    carId: int
    date: date
    valid: bool

    model_config = ConfigDict(populate_by_name=True)