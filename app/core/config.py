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
    user_password_max_len: int = 128
    # Регулярное выражение для проверки
    # правила пароля (например: минимум 1 буква, 1 цифра и 1 спецсимвол)
    password_pattern: str = (
        r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        )
    phone_pattern: str = r'^\+7\d{10}$'
    date_pattern: str = r'^\d{4}-\d{2}-\d{2}$'

    logging_format: str = '%(asctime)s - %(levelname)s - %(message)s'
    logging_dt_format: str = '%Y-%m-%d %H:%M:%S'

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
    NAME_MAX_LEN = 50
    STRING_LEN = 120
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
