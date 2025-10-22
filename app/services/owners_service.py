from app.db.base import datab as db
from app.db.models import Owner
from app.api.errors import NotFoundError

def list_owners():
    return Owner.query.all()

def create_owner(data: dict):
    owner = Owner(**data)
    db.session.add(owner)
    db.session.commit()
    return owner

def get_owner(owner_id: int):
    owner = Owner.query.get(owner_id)
    if not owner:
        raise NotFoundError("Owner not found")
    return owner