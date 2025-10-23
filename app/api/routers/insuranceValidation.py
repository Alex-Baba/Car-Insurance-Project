from flask.views import MethodView
from flask_smorest import Blueprint
from flask import request
from pydantic import ValidationError
from app.api.schemas import InsuranceValiditySchema,InsuranceValidityQuery
from app.services.validity_service import check_insurance

insurance_validation_bp = Blueprint('insurance_validation', __name__, url_prefix='/api/cars')

@insurance_validation_bp.route('/<int:car_id>/insurance-valid')
class InsuranceValidResource(MethodView):
    @insurance_validation_bp.response(200, InsuranceValiditySchema)
    def get(self, car_id):
        date_str = request.args.get("date")
        if not date_str:
            return {"error": "Missing query parameter 'date'", "field": "date"}, 400
        try:
            model = InsuranceValidityQuery(carId=car_id, date=date_str)
        except ValidationError as ve:
            return {"error": "Invalid date", "details": ve.errors()}, 422
        result = check_insurance(model.carId, model.date)
        return result, 200