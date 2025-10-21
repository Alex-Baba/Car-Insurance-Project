from marshmallow import Schema, fields

class OwnerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=False)

class InsurancePolicySchema(Schema):
    id = fields.Int(dump_only=True)
    provider = fields.Str(required=True)
    start_date = fields.Date()
    end_date = fields.Date()
    car_id = fields.Int(required=True)

class ClaimsSchema(Schema):
    id = fields.Int(dump_only=True)
    claim_date = fields.Date(required=True)
    description = fields.Str(required=True)
    amount = fields.Decimal(as_string=True)
    created_at = fields.DateTime(dump_only=True)
    car_id = fields.Int(required=True)

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

class InsuranceValiditySchema(Schema):
    carId = fields.Int(required=True)
    date = fields.Date(required=True)
    valid = fields.Bool(required=True)