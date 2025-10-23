from app.db.models import InsurancePolicy, Claim, Car
from app.db.base import datab as db
from app.api.errors import NotFoundError

def car_history(car_id: int):
    car = db.session.get(Car, car_id)
    if not car:
        raise NotFoundError("Car not found")
    policies = InsurancePolicy.query.filter_by(car_id=car_id).all()
    claims = Claim.query.filter_by(car_id=car_id).all()
    # Return raw date objects; Marshmallow ISODateField will serialize them.
    entries = [
        {
            "type": "POLICY",
            "policyId": p.id,
            "startDate": p.start_date,
            "endDate": p.end_date,
            "provider": p.provider
        } for p in policies
    ] + [
        {
            "type": "CLAIM",
            "claimId": c.id,
            "claimDate": c.claim_date,
            "amount": getattr(c, "amount", None),
            "description": getattr(c, "description", None)
        } for c in claims
    ]
    entries.sort(key=lambda e: e.get("startDate") or e.get("claimDate") or e.get("endDate"))
    return entries