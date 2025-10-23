from flask.views import MethodView
from flask_smorest import Blueprint
from flask import request, url_for
from app.db.models import InsurancePolicy
from app.api.schemas import PolicyCreate, PolicyUpdate, PolicyOut
from app.services.policies_service import list_policies, create_policy, update_policy, get_policy
from app.api.errors import ConflictError, DomainValidationError, NotFoundError

policies_bp = Blueprint('policies', __name__, url_prefix='/api', description='Insurance policies: global listing, creation, per-car listing, update and deletion.')

def _to_json(p: InsurancePolicy):
    """Serialize an InsurancePolicy ORM instance to primitive dict via Pydantic model.

    Pydantic v2 requires from_attributes=True for ORM objects; omission was causing 500s in tests.
    """
    return PolicyOut.model_validate(p, from_attributes=True).model_dump(by_alias=False)

# Canonical global collection: /api/policies (list all or create for a car by carId in body)
@policies_bp.route('/policies')
class InsurancePolicyCollection(MethodView):
    """Global policies collection.

    GET returns all policies (pagination TBD).
    POST creates a policy; body must include carId.
    """
    def get(self):
        return [_to_json(p) for p in list_policies()], 200

    def post(self):
        data = request.get_json(force=True, silent=True) or {}
        try:
            body = PolicyCreate.model_validate(data)
        except Exception as e:
            if hasattr(e, "errors"):
                errs = [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in e.errors()]
                return {"status": 422, "title": "Validation Error", "errors": errs}, 422
            return {"status": 400, "title": "Bad Request", "detail": str(e)}, 400
        try:
            p = create_policy(body.provider, body.startDate, body.endDate, body.carId)
        except ConflictError as ce:
            return {"status": 409, "title": "Conflict", "detail": ce.message}, 409
        except DomainValidationError as ve:
            return {"status": 400, "title": "Validation Error", "detail": ve.message, "field": getattr(ve, 'field', None)}, 400
        except NotFoundError as nf:
            return {"status": 404, "title": "Not Found", "detail": nf.message}, 404
        except Exception as e:
            return {"status": 500, "title": "Internal Server Error", "detail": str(e)}, 500
        headers = {'Location': f"/api/policies/{p.id}"}
        return _to_json(p), 201, headers


# Nested car-specific collection: /api/cars/<car_id>/policies
@policies_bp.route('/cars/<int:car_id>/policies')
class CarPoliciesCollection(MethodView):
    def get(self, car_id: int):
        # Filter manually from list_policies (simple for now)
        return [_to_json(p) for p in list_policies() if p.car_id == car_id], 200

    def post(self, car_id: int):
        data = request.get_json(force=True, silent=True) or {}
        # Allow body to omit carId when nested
        if 'carId' not in data:
            data['carId'] = car_id
        try:
            body = PolicyCreate.model_validate(data)
        except Exception as e:
            if hasattr(e, "errors"):
                errs = [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in e.errors()]
                return {"status": 422, "title": "Validation Error", "errors": errs}, 422
            return {"status": 400, "title": "Bad Request", "detail": str(e)}, 400
        try:
            p = create_policy(body.provider, body.startDate, body.endDate, body.carId)
        except ConflictError as ce:
            return {"status": 409, "title": "Conflict", "detail": ce.message}, 409
        except DomainValidationError as ve:
            return {"status": 400, "title": "Validation Error", "detail": ve.message, "field": getattr(ve, 'field', None)}, 400
        except NotFoundError as nf:
            return {"status": 404, "title": "Not Found", "detail": nf.message}, 404
        except Exception as e:
            return {"status": 500, "title": "Internal Server Error", "detail": str(e)}, 500
        headers = {'Location': f"/api/policies/{p.id}"}
        return _to_json(p), 201, headers

@policies_bp.route('/policies/<int:policy_id>')
class InsurancePolicyItem(MethodView):
    def get(self, policy_id: int):
        p = get_policy(policy_id)
        return _to_json(p), 200

    def put(self, policy_id: int):
        data = request.get_json(force=True, silent=True) or {}
        try:
            body = PolicyUpdate.model_validate(data)
        except Exception as e:
            if hasattr(e, "errors"):
                errs = [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in e.errors()]
                return {"status": 422, "title": "Validation Error", "errors": errs}, 422
            return {"status": 400, "title": "Bad Request", "detail": str(e)}, 400
        try:
            p = update_policy(
                policy_id,
                provider=body.provider,
                start_date=body.startDate,
                end_date=body.endDate
            )
        except ConflictError as ce:
            return {"status": 409, "title": "Conflict", "detail": ce.message}, 409
        return _to_json(p), 200

    def delete(self, policy_id: int):
        from app.db.base import datab as db
        p = get_policy(policy_id)
        db.session.delete(p)
        db.session.commit()
        return "", 204
