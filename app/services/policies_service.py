from app.db.base import datab as db
from app.db.models import InsurancePolicy, Car
from app.api.errors import NotFoundError, DomainValidationError

def list_policies():
    return InsurancePolicy.query.all()

def get_policy(policy_id: int):
    p = db.session.get(InsurancePolicy, policy_id)
    if not p:
        raise NotFoundError("Policy not found")
    return p

def create_policy(provider, start_date, end_date, car_id):
    car = db.session.get(Car, car_id)
    if not car:
        raise NotFoundError("Car not found")
    if end_date < start_date:
        raise DomainValidationError("endDate must be >= startDate", field="endDate")
    # Overlap rule: no existing policy overlapping the new date range
    overlap = InsurancePolicy.query.filter(
        InsurancePolicy.car_id == car_id,
        InsurancePolicy.start_date <= end_date,
        InsurancePolicy.end_date >= start_date
    ).first()
    if overlap:
        raise DomainValidationError("Policy dates overlap existing policy", field="startDate")
    p = InsurancePolicy(provider=provider, start_date=start_date, end_date=end_date, car_id=car_id)
    db.session.add(p)
    db.session.commit()
    return p

def update_policy(policy_id, provider=None, start_date=None, end_date=None):
    p = get_policy(policy_id)
    new_start = start_date or p.start_date
    new_end = end_date or p.end_date
    if new_end < new_start:
        raise DomainValidationError("endDate must be >= startDate", field="endDate")
    # Overlap rule on update (exclude current policy id)
    overlap = InsurancePolicy.query.filter(
        InsurancePolicy.car_id == p.car_id,
        InsurancePolicy.id != p.id,
        InsurancePolicy.start_date <= new_end,
        InsurancePolicy.end_date >= new_start
    ).first()
    if overlap:
        raise DomainValidationError("Policy dates overlap existing policy", field="startDate")
    if provider is not None:
        p.provider = provider
    if start_date is not None:
        p.start_date = start_date
    if end_date is not None:
        p.end_date = end_date
    db.session.commit()
    return p