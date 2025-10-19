from datetime import date, datetime
import re
from typing import Optional

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, field_validator, Field

from app.core.config import settings
from app.core.constants import Constants
from app.schemas.validators import (
    validate_password_change,
    validate_password_strength
)


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
        if date_of_birth > date.today():
            raise ValueError('Дата рождения не может быть в будущем')
        return date_of_birth


class UserRead(UserBase, schemas.BaseUser[int]):
    first_name: str
    last_name: str
    email: EmailStr
    is_driver: bool
    is_assistant: bool
    is_administrator: bool
    created: datetime
    updated: datetime

    class Config:
        # Exclude the unwanted fields from the schema
        exclude = {'is_active', 'is_superuser', 'is_verified'}
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "first_name": "Alex",
                "last_name": "Fill",
                "date_of_birth": "1990-01-01",
                "phone": "+79031234567",
                "is_driver": True,
                "is_assistant": False,
                "is_administrator": False,
                "created": "2024-01-15T10:30:00Z",
                "updated": "2024-01-20T14:45:00Z"
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
    password_confirm: str = Field(
        ...,
        title='Password Confirm',
        description='Подтверждение пароля',
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
        return validate_password_strength(password)

    @field_validator('password_confirm')
    @classmethod
    def validate_password_confirm(cls, password_confirm: str, info) -> str:
        password = info.data.get('password', '')
        if password != password_confirm:
            raise ValueError('Пароли не совпадают')
        return password_confirm

    def model_dump(self, **kwargs):
        """Исключаем password_confirm из данных для сохранения в БД"""
        data = super().model_dump(**kwargs)
        data.pop('password_confirm', None)
        return data

    class Config:
        exclude = {'is_active', 'is_superuser', 'is_verified'}
        json_schema_extra = {
            'example': {
                'email': 'user@example.com',
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!',
                'first_name': 'Alex',
                'last_name': 'Fill',
                'date_of_birth': '1992-05-20',
                'phone': '+79031234567'
            }
        }


class UserChangePassword(BaseModel):
    '''Схема для смены пароля пользователя'''
    old_password: str = Field(
        ...,
        title='Old Password',
        description='Текущий пароль пользователя'
    )
    new_password: str = Field(
        ...,
        title='New Password',
        description='Новый пароль пользователя',
        min_length=settings.user_password_min_len,
        max_length=settings.user_password_max_len,
    )

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, password: str, info) -> str:
        # Получаем старый пароль из данных
        old_password = info.data.get('old_password', '')
        return validate_password_change(old_password, password)

    class Config:
        json_schema_extra = {
            'example': {
                'old_password': 'OldPass123!',
                'new_password': 'NewPass456!'
            }
        }


class UserResetPassword(BaseModel):
    '''Схема для сброса пароля пользователя'''
    email: EmailStr = Field(
        ...,
        title='Email',
        description='Email пользователя для сброса пароля'
    )

    class Config:
        json_schema_extra = {
            'example': {
                'email': 'user@example.com'
            }
        }


class UserUpdate(UserBase, schemas.BaseUserUpdate):
    email: Optional[EmailStr] = None
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

    class Config:
        json_schema_extra = {
            'example': {
                'email': 'new.mail@example.com',
                'first_name': 'Alex',
                'last_name': 'Fill',
                'date_of_birth': '1992-05-20',
                'phone': '+79031234567'
            }
        }
