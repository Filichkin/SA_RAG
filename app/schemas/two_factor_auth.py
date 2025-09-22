from pydantic import BaseModel, Field, field_validator

from app.core.constants import Constants
from app.schemas.validators import validate_code_type


class TwoFactorAuthRequest(BaseModel):
    """Схема для запроса двухфакторной аутентификации"""
    email: str = Field(
        ...,
        title='Email',
        description='Email пользователя'
    )
    password: str = Field(
        ...,
        title='Password',
        description='Пароль пользователя'
    )

    class Config:
        json_schema_extra = {
            'example': {
                'email': 'filichkin_a@mail.ru',
                'password': 'SecurePass123!'
            }
        }


class TwoFactorAuthResponse(BaseModel):
    """Схема ответа для двухфакторной аутентификации"""
    message: str = Field(
        ...,
        title='Message',
        description='Сообщение о результате операции'
    )
    temp_token: str = Field(
        ...,
        title='Temporary Token',
        description='Временный токен для второго этапа аутентификации'
    )

    class Config:
        json_schema_extra = {
            'example': {
                'message': 'Код отправлен на email',
                'temp_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
            }
        }


class TwoFactorAuthVerifyCode(BaseModel):
    """Схема для проверки кода двухфакторной аутентификации (только код)"""
    code: str = Field(
        ...,
        title='Code',
        description='6-значный код подтверждения',
        min_length=Constants.TWO_FA_CODE_LEN,
        max_length=Constants.TWO_FA_CODE_LEN
    )

    @field_validator('code')
    @classmethod
    def validate_code(cls, code: str) -> str:
        return validate_code_type(code)

    class Config:
        json_schema_extra = {
            'example': {
                'code': '123456'
            }
        }


class TwoFactorAuthTokenResponse(BaseModel):
    """Схема ответа с токеном после успешной 2FA"""
    access_token: str = Field(
        ...,
        title='Access Token',
        description='JWT токен доступа'
    )
    token_type: str = Field(
        default='bearer',
        title='Token Type',
        description='Тип токена'
    )

    class Config:
        json_schema_extra = {
            'example': {
                'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                'token_type': 'bearer'
            }
        }


class LogoutResponse(BaseModel):
    """Схема ответа для logout"""
    message: str = Field(
        ...,
        title='Message',
        description='Сообщение о результате операции'
    )

    class Config:
        json_schema_extra = {
            'example': {
                'message': 'Выход выполнен успешно'
            }
        }
