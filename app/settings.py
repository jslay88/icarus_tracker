import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    INVITE_CODE: str = os.getenv('INVITE_CODE', 'BETA-TEST')
    DB_USER: str = os.getenv('DB_USER', 'postgres')
    DB_PASS: str = os.getenv('DB_PASS', 'postgres')
    DB_HOST: str = os.getenv('DB_HOST', 'postgres')
    DB_PORT: int = int(os.getenv('DB_PORT', 5432))
    DB_NAME: str = os.getenv('DB_NAME', 'postgres')
    SQLALCHEMY_DATABASE_URI: str = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    if LOG_LEVEL not in ['DEBUG', 'INFO', 'WARNING', 'CRITICAL']:
        LOG_LEVEL = 'INFO'


settings = Settings()
