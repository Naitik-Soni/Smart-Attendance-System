from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Face Recognition Main Service"
    APP_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str

    # Security (we’ll use later)
    SECRET_KEY: str = "change-this-later"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings():
    return Settings()