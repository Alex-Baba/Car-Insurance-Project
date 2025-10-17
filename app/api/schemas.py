from marshmallow import marshmallow, fields

class carsSchema(Schema):
    id = fields.Int(required=True)
    vin = fields.Str(required=True)
    make = fields.Str(required=True)
    model = fields.Str(required=True)
    yearOfManufacture = fields.Int(required=True)

