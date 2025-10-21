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
    
    insurance_policies = db.relationship('InsurancePolicy', back_populates='car', lazy=True, cascade="all, delete-orphan")  

    claims = db.relationship('Claims', back_populates='car', lazy=True, cascade="all, delete-orphan")

class InsurancePolicy(db.Model):
    __tablename__ = 'insurance_policies'

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(), nullable=False)
    start_date = db.Column(db.Date(), nullable=True)
    end_date = db.Column(db.Date(), nullable=True)

    car_id = db.Column(db.Integer(), db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car', back_populates='insurance_policies', lazy='selectin')

class Claims(db.Model):
    __tablename__ = 'claims'

    id = db.Column(db.Integer, primary_key=True)
    claim_date = db.Column(db.Date(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now(), nullable=False)

    car_id = db.Column(db.Integer(), db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car', lazy='selectin')