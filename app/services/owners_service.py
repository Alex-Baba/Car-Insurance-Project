"""Service layer for Owner operations.

Provides simple CRUD helpers decoupled from Flask views. Keeping DB interaction
here isolates persistence logic from request validation / response formatting.
"""

from app.db.base import datab as db
from app.db.models import Owner
from app.api.errors import NotFoundError

def list_owners():
    """Return all owners.

    For large datasets consider adding pagination; current tests assume full list.
    """
    return Owner.query.all()

def create_owner(data: dict):
    """Persist and return a new Owner instance."""
    owner = Owner(**data)
    db.session.add(owner)
    db.session.commit()
    return owner

def get_owner(owner_id: int):
    """Fetch an owner by primary key or raise NotFoundError if it does not exist."""
    owner = db.session.get(Owner, owner_id)
    if not owner:
        raise NotFoundError("Owner not found")
    return owner