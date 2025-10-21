from flask import Flask
from flask_smorest import Api
import os

from app.db.base import datab as db
from flask_migrate import Migrate

from app.api.routers.health import health_bp
from app.api.routers.cars import bp as cars_bp
from app.api.routers.owner import owner_bp
from app.api.routers.policies import policies_bp
from app.api.routers.claims import claims_bp
from app.api.routers.history import history_bp
from app.api.routers.insuranceValidation import insurance_validation_bp


def create_app(db_url=None):
   
    app = Flask(__name__)

    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['API_TITLE'] = 'Cars Insurance API'
    app.config['API_VERSION'] = 'v1'
    app.config['OPENAPI_VERSION'] = '3.0.3'
    app.config['OPENAPI_URL_PREFIX'] = '/'
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv('DATABASE_URL','sqlite:///data.db')
    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app) # initialise the API with the app

    #with app.app_context():
    #    db.create_all()  # create tables for our models

    api.register_blueprint(health_bp)
    api.register_blueprint(cars_bp)
    api.register_blueprint(owner_bp)
    api.register_blueprint(policies_bp)
    api.register_blueprint(claims_bp)
    api.register_blueprint(history_bp)
    api.register_blueprint(insurance_validation_bp)


    return app