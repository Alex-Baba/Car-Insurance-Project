from flask import Flask
from flask_smorest import Api
from flask_migrate import Migrate
from app.db.base import datab as db
from app.core.config import get_config
from app.core.logging import setup_logging, get_logger
from app.core.request_id import init_request_id

from app.api.errors import register_error_handlers
from app.api.routers.health import health_bp
from app.api.routers.cars import bp as cars_bp
from app.api.routers.owner import owner_bp
from app.api.routers.policies import policies_bp
from app.api.routers.claims import claims_bp
from app.api.routers.history import history_bp
from app.api.routers.insuranceValidation import insurance_validation_bp

def create_app(db_url=None):
    setup_logging()
    logger = get_logger()
    app = Flask(__name__)
    cfg = get_config()
    app.config.from_object(cfg)

    # Ensure SQLALCHEMY_DATABASE_URI always present
    if db_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    elif 'SQLALCHEMY_DATABASE_URI' not in app.config:
        app.config['SQLALCHEMY_DATABASE_URI'] = cfg.DATABASE_URL

    db.init_app(app)
    Migrate(app, db)
    register_error_handlers(app)
    init_request_id(app, logger)

    api = Api(app)
    api.register_blueprint(health_bp)
    api.register_blueprint(cars_bp)
    api.register_blueprint(owner_bp)
    api.register_blueprint(policies_bp)
    api.register_blueprint(claims_bp)
    api.register_blueprint(history_bp)
    api.register_blueprint(insurance_validation_bp)

    logger.info("app.started", env=cfg.APP_ENV)
    return app