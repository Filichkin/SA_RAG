from datetime import date
import re
from typing import Optional

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, field_validator, Field

from app.core.config import Constants, settings


class UserBase(BaseModel):
    """Базовый класс с общими полями и валидаторами для пользователей"""

    date_of_birth: Optional[date] = Field(
        default=None,
        title='Date of Birth',
        description='Формат: YYYY-MM-DD',
    )
    phone: Optional[str] = Field(
        default=None,
        title='Phone Number',
    )

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, phone: Optional[str]) -> Optional[str]:
        if phone is None or phone.strip() == '':
            return None
        phone = phone.strip()
        if not re.fullmatch(settings.phone_pattern, phone):
            raise ValueError(
                'Телефон должен быть в формате +7XXXXXXXXXX (11 цифр)'
            )
        return phone

    @field_validator('date_of_birth')
    @classmethod
    def validate_date_format(
        cls,
        date_of_birth: Optional[date]
    ) -> Optional[date]:
        if date_of_birth is None:
            return None
        # Проверяем, что дата не в будущем
        if date_of_birth > date.today():
            raise ValueError('Дата рождения не может быть в будущем')
        return date_of_birth


class UserRead(UserBase, schemas.BaseUser[int]):

    first_name: str = Field(..., max_length=Constants.NAME_MAX_LEN)
    last_name: str = Field(..., max_length=Constants.NAME_MAX_LEN)
    email: EmailStr

    class Config:
        # Exclude the unwanted fields from the schema
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "date_of_birth": "1990-01-01",
                "phone": "+1234567890",
            }
        }


class UserCreate(UserBase, schemas.BaseUserCreate):
    email: EmailStr
    password: str = Field(
        ...,
        title='Password',
        min_length=settings.user_password_min_len,
        max_length=settings.user_password_max_len,
    )
    first_name: str = Field(
        ...,
        title='First Name',
        description='First Name',
        min_length=Constants.NAME_MIN_LEN,
        max_length=Constants.NAME_MAX_LEN,
    )
    last_name: str = Field(
        ...,
        title='Last Name',
        description='Last Name',
        min_length=Constants.NAME_MIN_LEN,
        max_length=Constants.NAME_MAX_LEN,
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not password:
            raise ValueError('Пароль обязателен')

        password = password.strip()
        if len(password) < settings.user_password_min_len:
            raise ValueError(
                f'Пароль должен содержать минимум '
                f'{settings.user_password_min_len} символов'
                )
        if len(password) > settings.user_password_max_len:
            raise ValueError(
                f'Пароль должен содержать не более '
                f'{settings.user_password_max_len} символов'
                )

        if not re.fullmatch(settings.password_pattern, password):
            raise ValueError(
                'Пароль не соответствует требованиям безопасности: '
                'минимум 1 буква, 1 цифра и 1 спецсимвол)'
                )

        return password

    class Config:
        exclude = {'is_active', 'is_superuser', 'is_verified'}
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "first_name": "Alex",
                "last_name": "Fill",
                "date_of_birth": "1992-05-20",
                "phone": "+79031234567"
            }
        }


class UserUpdate(UserBase, schemas.BaseUserUpdate):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(
        default=None,
        title='Password',
        min_length=settings.user_password_min_len,
        max_length=settings.user_password_max_len,
    )
    first_name: Optional[str] = Field(
        default=None,
        title='First Name',
        description='First Name',
        min_length=Constants.NAME_MIN_LEN,
        max_length=Constants.NAME_MAX_LEN,
    )
    last_name: Optional[str] = Field(
        default=None,
        title='Last Name',
        description='Last Name',
        min_length=Constants.NAME_MIN_LEN,
        max_length=Constants.NAME_MAX_LEN,
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, password: Optional[str]) -> Optional[str]:
        # Пароль на апдейте опционален: проверяем только если пришёл непустой
        if password is None:
            return None
        password = password.strip()
        if password == '':
            return None

        if len(password) < settings.user_password_min_len:
            raise ValueError(
                f'Пароль должен содержать минимум '
                f'{settings.user_password_min_len} символов'
            )
        if len(password) > settings.user_password_max_len:
            raise ValueError(
                f'Пароль должен содержать не более '
                f'{settings.user_password_max_len} символов'
            )

        if not re.fullmatch(settings.password_pattern, password):
            raise ValueError(
                'Пароль не соответствует требованиям безопасности: '
                'минимум 1 буква, 1 цифра и 1 спецсимвол'
            )
        return password

    class Config:
        json_schema_extra = {
            "example": {
                "email": "new.mail@example.com",
                "first_name": "Alex",
                "last_name": "Fill",
                "date_of_birth": "1992-05-20",
                "phone": "+79031234567",
                "password": "Newpass1!"
            }
        }
