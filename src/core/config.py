from logging import config as logging_config
from pathlib import Path
from typing import Optional

from pydantic import PostgresDsn, EmailStr
from pydantic_settings import BaseSettings

from .logger import LOGGING

logging_config.dictConfig(LOGGING)


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / '.env'


class Settings(BaseSettings):
    project_title: str
    project_name: str
    database_dsn: PostgresDsn
    secret: str
    host: str
    port: int

    first_superuser_email: EmailStr = 'admin@example.com'
    first_superuser_password: str = '12345'

    class Config:
        env_file = ENV_FILE_PATH


settings = Settings()
