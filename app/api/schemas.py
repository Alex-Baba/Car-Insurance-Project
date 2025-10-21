from marshmallow import Schema, fields
from marshmallow import fields


class OwnerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=False)

class InsurancePolicySchema(Schema):
    id = fields.Int(dump_only=True)
    provider = fields.Str(required=True)
    start_date = fields.Date(required=False)
    end_date = fields.Date(required=False)

    car_id = fields.Int(required=True)

class ClaimsSchema(Schema):
    id = fields.Int(dump_only=True)
    claim_date = fields.Date(required=True)
    description = fields.Str(required=True)
    amount = fields.Decimal(as_string=True, required=True)
    created_at = fields.DateTime(dump_only=True)

    car_id = fields.Int(required=True)

class CarSchema(Schema):
    id = fields.Int(dump_only=True)
    vin = fields.Str(required=True)
    make = fields.Str(required=True)
    model = fields.Str(required=True)
    year_of_manufacture = fields.Int(required=True)

    owner = fields.Nested(OwnerSchema, required=True, allow_none=True)
    insurance_policies = fields.List(fields.Nested(InsurancePolicySchema), dump_only=True, attribute="insurance_policies")
    claims = fields.List(fields.Nested(ClaimsSchema), dump_only=True, attribute="claims")

class CarInputSchema(Schema):
    id= fields.Int(dump_only=True)
    vin = fields.Str(required=True)
    make = fields.Str(required=True)
    model = fields.Str(required=True)
    year_of_manufacture = fields.Int(required=True)

    owner_id = fields.Int(required=True)


class deleteCarSchema(Schema):
    id = fields.Int(required=True)

class HistorySchema(Schema):
    policies = fields.List(fields.Nested(InsurancePolicySchema))
    claims = fields.List(fields.Nested(ClaimsSchema))

class InsuranceValiditySchema(Schema):
    carId = fields.Int(required=True)
    date = fields.Date(required=True)
    valid = fields.Bool(required=True)

