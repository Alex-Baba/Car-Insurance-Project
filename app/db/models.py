

class Owner(db.Model):
    __tablename__ = 'owner'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=True)
    cars = db.relationship('Car', backref='owner', lazy=True)

class Car(db.Model):
    __tablename__ = 'car'

    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(), unique=True, nullable=False)
    make = db.Column(db.String(), nullable=True)
    model = db.Column(db.String(), nullable=True)
    year_of_manufacture = db.Column(db.Integer(), nullable=True)
    owner_id = db.Column(db.Integer(), db.ForeignKey('owner.id'), nullable=False)