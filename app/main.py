from flask import Flask
from flask_smorest import Api
from flask_migrate import Migrate
from app.db.base import datab as db
from app.core.config import get_config

from app.api.routers.health import health_bp
from app.api.routers.cars import car_bp
from app.api.routers.cars import bp as cars_bp
from app.api.routers.owner import owner_bp
from app.api.routers.policies import policies_bp
from app.api.routers.claims import claims_bp
from app.api.routers.history import history_bp
from app.api.routers.insuranceValidation import insurance_validation_bp
from app.api.errors import register_error_handlers


def create_app(db_url=None):
    app = Flask(__name__)
    cfg = get_config()
    app.config.from_object(cfg)
    if db_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url

    db.init_app(app)
    Migrate(app, db)

    register_error_handlers(app)

    api = Api(app)
    api.register_blueprint(health_bp)
    api.register_blueprint(car_bp)
    api.register_blueprint(cars_bp)
    api.register_blueprint(owner_bp)
    api.register_blueprint(policies_bp)
    api.register_blueprint(claims_bp)
    api.register_blueprint(history_bp)
    api.register_blueprint(insurance_validation_bp)
    return app