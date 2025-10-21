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
    PAGE_SIZE_DEFAULT = int(os.getenv('PAGE_SIZE_DEFAULT', '50'))
    ENABLE_SWAGGER = os.getenv('ENABLE_SWAGGER', '1') == '1'

    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data.db')
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return self.DATABASE_URL

class DevConfig(BaseConfig):
    DEBUG = True

class ProdConfig(BaseConfig):
    DEBUG = False

def get_config():
    env = os.getenv('APP_ENV', 'dev').lower()
    return ProdConfig() if env == 'prod' else DevConfig()