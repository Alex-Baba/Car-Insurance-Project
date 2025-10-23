from flask.views import MethodView
from flask_smorest import Blueprint
from pydantic import ValidationError
from app.api.schemas import CarCreate, CarUpdate, CarOut
from app.services.car_service import list_cars, create_car, get_car, update_car, delete_car
from app.api.errors import DomainValidationError
from app.core.logging import get_logger

bp = Blueprint('cars', __name__, url_prefix='/api/cars', description='Cars resource: manage vehicles linked to owners; cascade delete related policies and claims.')

@bp.route('/')
class CarsCollection(MethodView):
    """Collection resource for listing and creating cars."""
    def get(self):
        """Return all cars with embedded owner info (if loaded)."""
        cars = list_cars()
        # include owner nested if loaded
        out = []
        for c in cars:
            model = CarOut.model_validate(c, from_attributes=True)
            data = model.model_dump(by_alias=True)
            # embed owner object manually if relationship present
            if getattr(c, 'owner', None):
                data['owner'] = {
                    'id': c.owner.id,
                    'name': c.owner.name,
                    'email': c.owner.email
                }
            out.append(data)
        return out, 200

    def post(self):
        """Validate request body and create a new car, returning the created resource."""
        from flask import request
        json_data = request.get_json(silent=True) or {}
        logger = get_logger()
        logger.info("car.create.request", payload=json_data)
        try:
            body = CarCreate.model_validate(json_data)
        except ValidationError as ve:
            logger.warning("car.create.validation_error", errors=ve.errors())
            raise DomainValidationError("Invalid car payload", field="body", detail=ve.errors())
        car = create_car({
            "vin": body.vin,
            "make": body.make,
            "model": body.model,
            "year_of_manufacture": body.year_of_manufacture,
            "owner_id": body.owner_id
        })
        model = CarOut.model_validate(car, from_attributes=True)
        data = model.model_dump(by_alias=True)
        # Ensure camelCase keys for output consistency
        if 'year_of_manufacture' in data and 'yearOfManufacture' not in data:
            data['yearOfManufacture'] = data.pop('year_of_manufacture')
        if 'owner_id' in data and 'ownerId' not in data:
            data['ownerId'] = data.pop('owner_id')
        if getattr(car, 'owner', None):
            data['owner'] = {
                'id': car.owner.id,
                'name': car.owner.name,
                'email': car.owner.email
            }
        logger.info("car.create.success", car_id=car.id)
        from flask import jsonify
        resp = jsonify(data)
        resp.status_code = 201
        resp.headers['Location'] = f"/api/cars/{car.id}"
        return resp

@bp.route('/<int:car_id>')
class CarItem(MethodView):
    """Item resource for retrieving, updating and deleting a specific car."""
    def get(self, car_id):
        """Fetch a single car by id."""
        car = get_car(car_id)
        model = CarOut.model_validate(car, from_attributes=True)
        data = model.model_dump(by_alias=True)
        if 'year_of_manufacture' in data and 'yearOfManufacture' not in data:
            data['yearOfManufacture'] = data.pop('year_of_manufacture')
        if 'owner_id' in data and 'ownerId' not in data:
            data['ownerId'] = data.pop('owner_id')
        if getattr(car, 'owner', None):
            data['owner'] = {
                'id': car.owner.id,
                'name': car.owner.name,
                'email': car.owner.email
            }
        return data, 200

    def put(self, car_id):
        """Update mutable car fields; ignores None values."""
        from flask import request
        json_data = request.get_json() or {}
        try:
            body = CarUpdate.model_validate(json_data)
        except ValidationError as ve:
            raise DomainValidationError("Invalid car update", field="body", detail=ve.errors())
        car = update_car(
            car_id,
            vin=body.vin,
            make=body.make,
            model=body.model,
            year_of_manufacture=body.year_of_manufacture
        )
        model = CarOut.model_validate(car, from_attributes=True)
        data = model.model_dump(by_alias=True)
        if getattr(car, 'owner', None):
            data['owner'] = {
                'id': car.owner.id,
                'name': car.owner.name,
                'email': car.owner.email
            }
        return data, 200

    def delete(self, car_id):
        """Delete the car (cascades to policies/claims via ORM configuration)."""
        delete_car(car_id)
        return "", 204