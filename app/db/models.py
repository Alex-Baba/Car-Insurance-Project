from app.db.base import datab as db

class Owner(db.Model):
    __tablename__ = 'owner'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=True)
    
    cars = db.relationship('Car', back_populates='owner', lazy=True, cascade="all, delete-orphan")

class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(), unique=True, nullable=False)
    make = db.Column(db.String(), nullable=True)
    model = db.Column(db.String(), nullable=True)
    year_of_manufacture = db.Column(db.Integer, nullable=True)

    owner_id = db.Column(db.Integer(), db.ForeignKey('owner.id'), nullable=False)
    owner = db.relationship('Owner', back_populates='cars', lazy=True)