from datetime import datetime
import re
from typing import Annotated, Optional

from fastapi_users import schemas
from pydantic import EmailStr, field_validator, Field, StringConstraints

from app.core.config import Constants, settings


PasswordStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=settings.user_password_min_len,
        pattern=settings.password_pattern,
        max_length=settings.user_password_max_len,
        )
    ]


class UserRead(schemas.BaseUser[int]):

    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    EmailStr: EmailStr
    date_of_birth: datetime | None = None
    phone: str | None = None

    class Config:
        # Exclude the unwanted fields from the schema
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "phone": "+1234567890",
            }
        }


class UserCreate(schemas.BaseUserCreate):
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
    date_of_birth: Annotated[
        Optional[datetime],
        Field(
            title='Date of Birth',
        ),
    ]
    phone: Annotated[
        Optional[str],
        Field(
            title='Phone Number',
        ),
    ]

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


class UserUpdate(schemas.BaseUserUpdate):
    pass
