from datetime import datetime, time
from sqlalchemy import and_
from app.db.base import datab as db
from app.db.models import InsurancePolicy
from app.core.logging import get_logger

log = get_logger()

def log_today_expiring_policies() -> int:
    now = datetime.now()
    today = now.date()
    window_start = datetime.combine(today, time(0, 0))
    window_end = datetime.combine(today, time(1, 0))
    # Only run logging inside midnight window
    if not (window_start <= now < window_end):
        return 0

    policies = (InsurancePolicy.query
                .filter(and_(
                    InsurancePolicy.end_date == today,
                    InsurancePolicy.logged_expiry_at.is_(None)
                )).all())

    if not policies:
        return 0

    count = 0
    for p in policies:
        p.logged_expiry_at = now
        log.info("policy.expiry",
                 policy_id=p.id,
                 car_id=p.car_id,
                 end_date=p.end_date.isoformat(),
                 logged_at=now.isoformat())
        count += 1

    db.session.commit()
    return count