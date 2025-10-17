from flask import Flask
from flask_smorest import Api
import os

from db.base import datab as db

from api.routers.health import health_bp
from api.routers.cars import bp as cars_bp
from api.routers.claims import bp as claims_bp


def create_app(db_url=None):
   
    app = Flask(__name__)

    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['API_TITLE'] = 'Cars Insurance API'
    app.config['API_VERSION'] = 'v1'
    app.config['OPENAPI_VERSION'] = '3.0.3'
    app.config['OPENAPI_URL_PREFIX'] = '/'
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL','sqlite:///data.db')
    db.init_app(app)

    api = Api(app) # initialise the API with the app

    with app.app_context():
        db.create_all()  # create tables for our models

    api.register_blueprint(health_bp)
    api.register_blueprint(cars_bp)
    api.register_blueprint(claims_bp)

    return app