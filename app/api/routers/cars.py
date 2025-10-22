from flask.views import MethodView
from flask_smorest import Blueprint
from app.api.schemas import CarSchema, CarInputSchema, DeleteCarSchema
from app.services.car_service import list_cars, create_car, get_car, delete_car

bp = Blueprint('cars', __name__, url_prefix='/api/cars')
car_bp=Blueprint('car', __name__, url_prefix='/api/car')

@bp.route('/')
class CarsCollection(MethodView):
    @bp.response(200, CarSchema(many=True))
    def get(self):
        return list_cars()

    @bp.arguments(CarInputSchema)
    @bp.response(201, CarSchema)
    def post(self, data):
        return create_car(data)

@bp.route('/<int:car_id>')
class CarItem(MethodView):
    @bp.response(200, CarSchema)
    def get(self, car_id):
        return get_car(car_id)

    @bp.arguments(DeleteCarSchema)
    @bp.response(204)
    def delete(self, data, car_id):
        delete_car(car_id)
        return ""