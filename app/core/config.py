from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    APP_ENV: str = Field(default='dev')
    DATABASE_URL: str = Field(default='sqlite:///data.db')
    SECRET_KEY: str = Field(default='change-me')

    # Logging
    LOG_LEVEL: str = Field(default='INFO')
    LOG_FILE: str = Field(default='app.log')
    LOG_MAX_BYTES: int = Field(default=2_097_152)
    LOG_BACKUP_COUNT: int = Field(default=10)
    LOG_TO_FILE: bool = Field(default=True)

    # Swagger / OpenAPI (needed by flask-smorest)
    API_TITLE: str = Field(default='Cars Insurance API')
    API_VERSION: str = Field(default='v1')
    OPENAPI_VERSION: str = Field(default='3.0.3')
    ENABLE_SWAGGER: bool = Field(default=True)

    PAGE_SIZE_DEFAULT: int = Field(default=50)

    # Scheduler
    SCHEDULER_ENABLED: bool = Field(default=False)
    EXPIRY_JOB_INTERVAL_MINUTES: int = Field(default=10)

@lru_cache
def get_settings() -> Settings:
    return Settings()

def apply_flask_config(app, settings: Settings):
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['API_TITLE'] = settings.API_TITLE
    app.config['API_VERSION'] = settings.API_VERSION
    app.config['OPENAPI_VERSION'] = settings.OPENAPI_VERSION
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    app.config['OPENAPI_URL_PREFIX'] = '/' if settings.ENABLE_SWAGGER else None