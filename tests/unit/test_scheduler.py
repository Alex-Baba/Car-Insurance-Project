from datetime import datetime, date, time, timedelta
import pytest
from app.db.base import datab as db
from app.db.models import InsurancePolicy
from app.services.expiry_service import log_today_expiring_policies

class FakeDateTime(datetime):
    _fixed = None
    @classmethod
    def set(cls, dt):
        cls._fixed = dt
    @classmethod
    def now(cls, tz=None):
        return cls._fixed
    @classmethod
    def combine(cls, d, t):
        # ensure we return a real datetime, not FakeDateTime, to avoid side-effects
        return datetime.combine(d, t)

def patch_datetime(monkeypatch, fixed_dt):
    from app.services import expiry_service as svc
    FakeDateTime.set(fixed_dt)
    monkeypatch.setattr(svc, "datetime", FakeDateTime)

@pytest.fixture
def policy_today(car_factory):
    car = car_factory()
    p = InsurancePolicy(
        car_id=car.id,
        provider="Sched",
        start_date=date.today(),
        end_date=date.today()
    )
    db.session.add(p)
    db.session.commit()
    return p

@pytest.fixture
def policy_tomorrow(car_factory):
    car = car_factory()
    p = InsurancePolicy(
        car_id=car.id,
        provider="Sched",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1)
    )
    db.session.add(p)
    db.session.commit()
    return p

def test_scheduler_marks_today(monkeypatch, app, policy_today):
    with app.app_context():
        # Inside window (00:30)
        patch_datetime(monkeypatch, datetime.combine(date.today(), time(0, 30)))
        count = log_today_expiring_policies()
        updated = InsurancePolicy.query.get(policy_today.id)
        assert count == 1
        assert updated.logged_expiry_at is not None

        # Second run same window: should not relog (idempotent)
        count2 = log_today_expiring_policies()
        assert count2 == 0

def test_scheduler_skips_non_today(monkeypatch, app, policy_tomorrow):
    with app.app_context():
        patch_datetime(monkeypatch, datetime.combine(date.today(), time(0, 30)))
        count = log_today_expiring_policies()
        updated = InsurancePolicy.query.get(policy_tomorrow.id)
        assert count == 0
        assert updated.logged_expiry_at is None

def test_scheduler_outside_window(monkeypatch, app, policy_today):
    with app.app_context():
        # Outside midnight window (e.g. 02:15)
        patch_datetime(monkeypatch, datetime.combine(date.today(), time(2, 15)))
        count = log_today_expiring_policies()
        updated = InsurancePolicy.query.get(policy_today.id)
        assert count == 0
        assert updated.logged_expiry_at is None