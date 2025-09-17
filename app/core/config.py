from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'SA_RAG Agent'
    description: str = 'Aplication for company search support'
    secret: str = 'SECRET'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None
    jwt_token_lifetime: int = 3600
    user_password_min_len: int = 8

    postgres_port: int
    postgres_password: str
    postgres_user: str
    postgres_db: str
    postgres_host: str

    class Config:
        env_file = '.env'


settings = Settings()


class Constants:
    AUTH_PREFIX = '/auth/jwt'
    AUTH_TAGS = ('auth',)
    REGISTER_PREFIX = '/auth'
    USERS_PREFIX = '/users'
    USERS_TAGS = ('users',)
    JWT_TOKEN_URL = 'auth/jwt/login'
    JWT_AUTH_BACKEND_NAME = 'jwt'
    NAME_MIN_LEN = 1
    NAME_MAX_LEN = 100
    RAG_ENDPOINTS_PREFIX = '/api'
    RAG_ENDPOINTS_TAGS = ('RAG_Agent',)


class Messages:
    PASSWORD_TOO_SHORT = (
        f'Password must be not less {settings.user_password_min_len}'
    )
    EMAIL_IN_PASSWORD = 'Password should`t contain email'
    USER_REGISTERED = 'User registered: '


def get_async_db_url() -> str:
    """Возвращает асинхронный URL для подключения к БД"""
    return (
        f'postgresql+asyncpg://{settings.postgres_user}:'
        f'{settings.postgres_password}@'
        f'{settings.postgres_host}:{settings.postgres_port}/'
        f'{settings.postgres_db}'
    )
