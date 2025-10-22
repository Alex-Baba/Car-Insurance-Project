from flask.views import MethodView
from flask_smorest import Blueprint
from flask_pydantic import validate
from app.api.schemas import CarSchema, CarCreate, CarUpdate
from app.services.car_service import list_cars, create_car, get_car, update_car, delete_car

bp = Blueprint('cars', __name__, url_prefix='/api/cars')

def _to_json(c):
    return {
        "id": c.id,
        "vin": c.vin,
        "make": c.make,
        "model": c.model,
        "year_of_manufacture": c.year_of_manufacture,
        "owner_id": c.owner_id
    }

@bp.route('/')
class CarsCollection(MethodView):
    @bp.response(200, CarSchema(many=True))
    def get(self):
        return list_cars()

    @validate()
    @bp.response(201, CarSchema)
    def post(self, body: CarCreate):
        car = create_car(
            body.vin,
            body.make,
            body.model,
            body.year_of_manufacture,
            body.owner_id
        )
        return car

@bp.route('/<int:car_id>')
class CarItem(MethodView):
    @bp.response(200, CarSchema)
    def get(self, car_id):
        return get_car(car_id)

    @validate()
    @bp.response(200, CarSchema)
    def put(self, car_id, body: CarUpdate):
        car = update_car(
            car_id,
            vin=body.vin,
            make=body.make,
            model=body.model,
            year_of_manufacture=body.year_of_manufacture
        )
        return car

    @bp.response(204)
    def delete(self, car_id):
        delete_car(car_id)
        return ""