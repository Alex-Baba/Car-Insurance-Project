"""Policy expiry logging service.

Responsible for idempotently logging policies that expire 'today'. Designed to be
called from a scheduled job (e.g., APScheduler) shortly after midnight. It only
logs during a guarded time window (00:00-00:59) to avoid duplicate daily runs
while still allowing retries inside the same hour.
"""

from datetime import datetime, time
from sqlalchemy import and_
from app.db.base import datab as db
from app.db.models import InsurancePolicy
from app.core.logging import get_logger

log = get_logger()

def log_today_expiring_policies() -> int:
    """Log each policy whose end_date is today and not previously logged.

    Returns the number of policies logged. If called outside the midnight window
    it returns 0 immediately. Uses a simple idempotency flag (logged_expiry_at).
    """
    now = datetime.now()
    today = now.date()
    window_start = datetime.combine(today, time(0, 0))
    window_end = datetime.combine(today, time(1, 0))
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
        log.info(
            "policy.expiry",
            policy_id=p.id,
            car_id=p.car_id,
            end_date=p.end_date.isoformat(),
            logged_at=now.isoformat()
        )
        count += 1

    db.session.commit()
    return count