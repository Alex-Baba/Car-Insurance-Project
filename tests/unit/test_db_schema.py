from sqlalchemy import inspect
from app.db.base import datab as db

def test_db_schema(app):
    with app.app_context():
        insp = inspect(db.engine)
        tables = set(insp.get_table_names())
        assert {"owner","car","insurance_policy","claim"}.issubset(tables)
        car_idx = {i["name"]: i for i in insp.get_indexes("car")}
        assert "ix_car_vin" in car_idx
        assert bool(car_idx["ix_car_vin"].get("unique")) is True