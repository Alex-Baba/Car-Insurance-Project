from app.db.models import InsurancePolicy, Claim, Car
from app.db.base import datab as db
from app.api.errors import NotFoundError

def car_history(car_id: int):
    """Aggregate a car's policies and claims into a unified chronological list."""
    car = db.session.get(Car, car_id)
    if not car:
        raise NotFoundError("Car not found")
    policies = InsurancePolicy.query.filter_by(car_id=car_id).all()
    claims = Claim.query.filter_by(car_id=car_id).all()
    # Build intermediate entries with a unified chronological key (chrono_date)
    raw_entries = []
    for p in policies:
        raw_entries.append({
            "type": "POLICY",
            "policyId": p.id,
            "startDate": p.start_date.isoformat(),
            "endDate": p.end_date.isoformat(),
            "provider": p.provider,
            "_chrono": p.start_date
        })
    for c in claims:
        raw_entries.append({
            "type": "CLAIM",
            "claimId": c.id,
            "claimDate": c.claim_date.isoformat(),
            "amount": getattr(c, "amount", None),
            "description": getattr(c, "description", None),
            "_chrono": c.claim_date
        })
    # Sort by real date object, then by type for stable deterministic order (POLICY before CLAIM if same day)
    raw_entries.sort(key=lambda e: (e["_chrono"], e["type"]))
    # Drop internal key
    for e in raw_entries:
        e.pop("_chrono", None)
    return raw_entries