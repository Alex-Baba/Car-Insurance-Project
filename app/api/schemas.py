from marshmallow import fields
from marshmallow import Schema


class OwnerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=False)

#trebuie sa faci schema separate pentru update sau post urgent
class CarSchema(Schema):
    id = fields.Int(dump_only=True)
    vin = fields.Str(required=True)
    make = fields.Str(required=True)
    model = fields.Str(required=True)
    year_of_manufacture = fields.Int(required=True)

    owner = fields.Nested(OwnerSchema, required=True, allow_none=True)

class CarInputSchema(Schema):
    id= fields.Int(dump_only=True)
    vin = fields.Str(required=True)
    make = fields.Str(required=True)
    model = fields.Str(required=True)
    year_of_manufacture = fields.Int(required=True)

    owner_id = fields.Int(required=True)


class deleteCarSchema(Schema):
    id = fields.Int(required=True)