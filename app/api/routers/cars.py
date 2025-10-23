"""Cars API endpoints.

Provides CRUD operations for cars. Uses Pydantic models for request validation
and manual embedding of owner data (relationship) in responses.
"""
from flask.views import MethodView
from flask_smorest import Blueprint
from pydantic import ValidationError
from app.api.schemas import CarCreate, CarUpdate, CarOut
from app.services.car_service import list_cars, create_car, get_car, update_car, delete_car
from app.api.errors import DomainValidationError

bp = Blueprint('cars', __name__, url_prefix='/api/cars')

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
        json_data = bp.app.current_request.json if hasattr(bp.app, 'current_request') else None  # fallback for flask context
        # use flask request
        from flask import request
        json_data = request.get_json() or {}
        try:
            body = CarCreate.model_validate(json_data)
        except ValidationError as ve:
            raise DomainValidationError("Invalid car payload", field="body", detail=ve.errors())
        car = create_car(
            body.vin,
            body.make,
            body.model,
            body.year_of_manufacture,
            body.owner_id
        )
        model = CarOut.model_validate(car, from_attributes=True)
        data = model.model_dump(by_alias=True)
        if getattr(car, 'owner', None):
            data['owner'] = {
                'id': car.owner.id,
                'name': car.owner.name,
                'email': car.owner.email
            }
        return data, 201

@bp.route('/<int:car_id>')
class CarItem(MethodView):
    """Item resource for retrieving, updating and deleting a specific car."""
    def get(self, car_id):
        """Fetch a single car by id."""
        car = get_car(car_id)
        model = CarOut.model_validate(car, from_attributes=True)
        data = model.model_dump(by_alias=True)
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