import os

class BaseConfig:
    PROPAGATE_EXCEPTIONS = True
    API_TITLE = 'Cars Insurance API'
    API_VERSION = 'v1'
    OPENAPI_VERSION = '3.0.3'
    OPENAPI_URL_PREFIX = '/'
    OPENAPI_SWAGGER_UI_PATH = '/swagger-ui'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    APP_ENV = os.getenv('APP_ENV', 'dev').lower()
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data.db')

    # Flask-SQLAlchemy expects this key
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

class DevConfig(BaseConfig):
    DEBUG = True

class ProdConfig(BaseConfig):
    DEBUG = False

def get_config():
    return ProdConfig() if os.getenv('APP_ENV', 'dev').lower() == 'prod' else DevConfig()