from flask.views import MethodView
from flask_smorest import Blueprint
from flask import request
from pydantic import ValidationError
from app.api.schemas import InsuranceValidityQuery, InsuranceValidityOut
from app.services.validity_service import check_insurance
from app.api.errors import DomainValidationError

insurance_validation_bp = Blueprint('insurance_validation', __name__, url_prefix='/api/cars')

@insurance_validation_bp.route('/<int:car_id>/insurance-valid')
class InsuranceValidResource(MethodView):
    def get(self, car_id):
        date_str = request.args.get("date")
        if not date_str:
            raise DomainValidationError("Missing query parameter 'date'", field="date")
        try:
            model = InsuranceValidityQuery(carId=car_id, date=date_str)
        except ValidationError:
            raise DomainValidationError("Invalid date", field="date")
        except ValueError as ve:
            # year range validator raises ValueError
            raise DomainValidationError(str(ve), field="date")
        result = check_insurance(model.carId, model.date)
        out = InsuranceValidityOut.model_validate(result)
        return out.model_dump(by_alias=True), 200