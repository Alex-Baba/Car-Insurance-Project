import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from asgiref.wsgi import WsgiToAsgi
from datetime import date
import itertools
import httpx

from app.main import create_app
from app.db.base import datab as db
from app.db.models import Owner, Car, InsurancePolicy, Claim

_vin_seq = itertools.count()

@pytest.fixture(scope="session")
def app():
    app = create_app(db_url="sqlite:///:memory:")
    with app.app_context():
        db.create_all()
    return app

@pytest.fixture(scope="session")
def asgi_app(app):
    return WsgiToAsgi(app)

# Clean DB before each test (keeps schema; avoids unique VIN collisions)
@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        yield
        db.session.rollback()

@pytest.fixture
def owner_factory():
    def f(name="John Doe", email="john@example.com"):
        o = Owner(name=name, email=email)
        db.session.add(o)
        db.session.commit()
        return o
    return f

@pytest.fixture
def car_factory(owner_factory):
    def f(**overrides):
        owner = overrides.pop("owner", None) or owner_factory()
        vin = overrides.pop("vin", f"VIN{next(_vin_seq):010d}")
        c = Car(
            vin=vin,
            make=overrides.pop("make", "Ford"),
            model=overrides.pop("model", "Focus"),
            year_of_manufacture=overrides.pop("year_of_manufacture", 2020),
            owner_id=owner.id,
            **overrides
        )
        db.session.add(c)
        db.session.commit()
        return c
    return f

@pytest.fixture
def policy_factory(car_factory):
    def f(car=None, start=None, end=None, provider="InsureCo"):
        car = car or car_factory()
        today = date.today()
        start = start or today
        end = end or today
        p = InsurancePolicy(car_id=car.id, provider=provider, start_date=start, end_date=end)
        db.session.add(p)
        db.session.commit()
        return p
    return f

@pytest.fixture
def claim_factory(car_factory):
    def f(car=None, claim_date=None, description="Crash", amount=1000):
        from datetime import date as _d
        car = car or car_factory()
        claim_date = claim_date or _d.today()
        cl = Claim(car_id=car.id, claim_date=claim_date, description=description, amount=amount)
        db.session.add(cl)
        db.session.commit()
        return cl
    return f

@pytest.fixture
def async_client(asgi_app):
    import httpx
    transport = httpx.ASGITransport(app=asgi_app)
    client = httpx.AsyncClient(transport=transport,
                               base_url="http://testserver",
                               follow_redirects=True)
    return client