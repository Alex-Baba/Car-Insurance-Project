from marshmallow import Schema, fields, ValidationError, validates_schema

def _validate_year_range(value):
    if value.year < 1900 or value.year > 2100:
        raise ValidationError("Year out of allowed range (1900-2100).")

class ISODateField(fields.Date):
    def _deserialize(self, value, attr, data, **kwargs):
        # Enforce exact pattern YYYY-MM-DD
        if not isinstance(value, str) or len(value) != 10:
            raise ValidationError("Date must be ISO format YYYY-MM-DD.")
        parts = value.split("-")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValidationError("Date must be ISO format YYYY-MM-DD.")
        try:
            date_obj = super()._deserialize(value, attr, data, **kwargs)
        except ValidationError:
            raise ValidationError("Date must be ISO format YYYY-MM-DD.")
        _validate_year_range(date_obj)
        return date_obj

class OwnerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=False)

class InsurancePolicySchema(Schema):
    id = fields.Int(dump_only=True)
    provider = fields.Str(required=True)
    start_date = ISODateField(required=True)
    end_date = ISODateField(required=True)
    car_id = fields.Int(required=True)

    @validates_schema
    def validate_dates(self, data, **_):
        sd = data.get("start_date")
        ed = data.get("end_date")
        if sd and ed and sd > ed:
            raise ValidationError({"end_date": "end_date must be >= start_date"})

class ClaimsSchema(Schema):
    id = fields.Int(dump_only=True)
    claim_date = ISODateField(required=True)
    description = fields.Str(required=True)
    amount = fields.Decimal(as_string=True, required=True)
    created_at = fields.DateTime(dump_only=True)
    car_id = fields.Int(required=True)

    @validates_schema
    def validate_claim_date(self, data, **_):
        cd = data.get("claim_date")
        if cd is None:
            return
        from datetime import date
        if cd > date.today():
            raise ValidationError({"claim_date": "claim_date cannot be in the future"})

    @validates_schema
    def validate_amount_and_description(self, data, **_):
        from decimal import Decimal, InvalidOperation
        desc = data.get("description")
        if desc is None or not desc.strip():
            raise ValidationError({"description": "description must be non-empty"})
        amt = data.get("amount")
        if amt is None:
            raise ValidationError({"amount": "amount is required"})
        try:
            if Decimal(amt) <= 0:
                raise ValidationError({"amount": "amount must be > 0"})
        except (InvalidOperation, TypeError):
            raise ValidationError({"amount": "amount must be a valid decimal > 0"})

class InsuranceValiditySchema(Schema):
    carId = fields.Int(required=True)
    date = ISODateField(required=True)
    valid = fields.Bool(required=True)

class CarSchema(Schema):
    id = fields.Int(dump_only=True)
    vin = fields.Str(required=True)
    make = fields.Str(required=True)
    model = fields.Str(required=True)
    year_of_manufacture = fields.Int(required=True)
    owner = fields.Nested(OwnerSchema, dump_only=True)
    insurance_policies = fields.List(fields.Nested(InsurancePolicySchema), dump_only=True)
    claims = fields.List(fields.Nested(ClaimsSchema), dump_only=True)

class CarInputSchema(Schema):
    vin = fields.Str(required=True)
    make = fields.Str(required=True)
    model = fields.Str(required=True)
    year_of_manufacture = fields.Int(required=True)
    owner_id = fields.Int(required=True)

class deleteCarSchema(Schema):
    id = fields.Int(required=True)

class HistoryEntrySchema(Schema):
    type = fields.Str(required=True)      # POLICY or CLAIM
    policyId = fields.Int()
    startDate = fields.Date()
    endDate = fields.Date()
    provider = fields.Str()
    claimId = fields.Int()
    claimDate = fields.Date()
    amount = fields.Decimal(as_string=True)
    description = fields.Str()