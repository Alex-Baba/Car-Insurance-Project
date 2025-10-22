from flask import Flask
from flask_smorest import Api
from flask_migrate import Migrate
from app.db.base import datab as db
from app.core.logging import setup_logging, get_logger
from app.core.request_id import init_request_id
from app.core.config import get_settings
from app.core.scheduling import start_expiry_scheduler, shutdown_expiry_scheduler
from app.api.errors import register_error_handlers
import os
from sqlalchemy import inspect

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
    settings = get_settings()

    app = Flask(__name__)
    # Minimal required config for flask-smorest
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['API_TITLE'] = settings.API_TITLE
    app.config['API_VERSION'] = settings.API_VERSION
    app.config['OPENAPI_VERSION'] = settings.OPENAPI_VERSION
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    # Add prefix (needed for swagger route)
    app.config['OPENAPI_URL_PREFIX'] = '/'
    if not settings.ENABLE_SWAGGER:
        app.config['OPENAPI_URL_PREFIX'] = None

    db.init_app(app)
    Migrate(app, db)
    register_error_handlers(app)
    init_request_id(app, logger)

    # Log existing tables
    with app.app_context():
        try:
            tables = inspect(db.engine).get_table_names()
            logger.info("db.tables", count=len(tables), tables=tables)
        except Exception as e:
            logger.warning("db.tables.error", error=str(e))

    api = Api(app)
    api.register_blueprint(health_bp)
    api.register_blueprint(cars_bp)
    api.register_blueprint(owner_bp)
    api.register_blueprint(policies_bp)
    api.register_blueprint(claims_bp)
    api.register_blueprint(history_bp)
    api.register_blueprint(insurance_validation_bp)

    if settings.SCHEDULER_ENABLED and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_expiry_scheduler()

    @app.teardown_appcontext
    def _shutdown(_exc=None):
        shutdown_expiry_scheduler()

    logger.info("app.started", env=settings.APP_ENV)
    return app