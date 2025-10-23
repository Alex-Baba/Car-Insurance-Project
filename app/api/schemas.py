from marshmallow import Schema, fields, ValidationError, validates_schema
from datetime import date
from pydantic import BaseModel, Field, field_validator, ConfigDict, condecimal

# ---- Marshmallow helpers ----
def _validate_year_range(d: date):
    if d.year < 1900 or d.year > 2100:
        raise ValidationError("Year out of allowed range (1900-2100).")

class ISODateField(fields.Date):
    def _deserialize(self, value, attr, data, **kwargs):
        dt = super()._deserialize(value, attr, data, **kwargs)
        _validate_year_range(dt)
        return dt

# ---- Marshmallow response schemas ----
class OwnerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str()

class CarSchema(Schema):
    id = fields.Int(dump_only=True)
    vin = fields.Str(required=True)
    make = fields.Str(required=True)
    model = fields.Str(required=True)
    year_of_manufacture = fields.Int(required=True)
    owner_id = fields.Int()
    owner = fields.Nested(OwnerSchema, dump_only=True)
    insurance_policies = fields.List(fields.Nested(lambda: InsurancePolicySchema()), dump_only=True)
    claims = fields.List(fields.Nested(lambda: ClaimsSchema()), dump_only=True)

class InsurancePolicySchema(Schema):
    id = fields.Int(dump_only=True)
    provider = fields.Str(required=True)
    start_date = ISODateField(required=True)
    end_date = ISODateField(required=True)
    car_id = fields.Int(required=True)

    @validates_schema
    def dates_ok(self, data, **_):
        sd, ed = data.get("start_date"), data.get("end_date")
        if sd and ed and ed < sd:
            raise ValidationError({"end_date": "end_date must be >= start_date"})

class ClaimsSchema(Schema):
    id = fields.Int(dump_only=True)
    # Provide both snake_case and camelCase for compatibility
    claim_date = ISODateField(required=True, data_key="claimDate")
    description = fields.Str(required=True)
    amount = fields.Decimal(required=True, as_string=True)
    car_id = fields.Int(required=True, data_key="carId")

    @validates_schema
    def claim_ok(self, data, **_):
        amt = data.get("amount")
        if amt is not None and amt <= 0:
            raise ValidationError({"amount": "amount must be > 0"})

class HistoryEntrySchema(Schema):
    type = fields.Str(required=True)  # POLICY or CLAIM
    policyId = fields.Int()
    startDate = ISODateField()
    endDate = ISODateField()
    provider = fields.Str()
    claimId = fields.Int()
    claimDate = ISODateField()
    amount = fields.Decimal(as_string=True)
    description = fields.Str()

class InsuranceValiditySchema(Schema):
    carId = fields.Int(required=True)
    date = ISODateField(required=True)
    valid = fields.Bool(required=True)

class DeleteCarSchema(Schema):
    id = fields.Int(required=True)

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