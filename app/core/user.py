import logging
from typing import Optional, Union

from fastapi import Depends, HTTPException, Request
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    IntegerIDMixin,
    InvalidPasswordException
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy
)
from fastapi_users.jwt import generate_jwt
import jwt
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import Constants, Messages
from app.core.db import get_async_session
from app.models.user import User
from app.schemas.user import UserCreate


async def get_user_db(
        session: AsyncSession = Depends(get_async_session)
):
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(
    tokenUrl=Constants.JWT_TOKEN_URL
)


class CustomJWTStrategy(JWTStrategy):
    '''Кастомная JWT стратегия с проверкой версии токена'''

    async def read_token(self, token: str, user_manager) -> Optional[User]:
        '''Читает токен и проверяет его валидность с учетом версии'''
        # Сначала используем базовую логику
        user = await super().read_token(token, user_manager)
        if not user:
            return None

        try:
            # Декодируем токен для проверки версии
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=['HS256'],
                audience=self.token_audience
            )

            # Получаем версию токена
            token_version = payload.get('token_version', 1)

            # Проверяем версию токена
            if user.token_version != token_version:
                return None

            return user

        except jwt.InvalidTokenError:
            return None

    async def write_token(self, user: User) -> str:
        '''Создает токен с версией пользователя'''
        data = {
            'sub': str(user.id),
            'token_version': user.token_version,
            'aud': self.token_audience,
        }
        return generate_jwt(
            data,
            self.secret,
            self.lifetime_seconds
        )


def get_jwt_strategy() -> CustomJWTStrategy:
    return CustomJWTStrategy(
        secret=settings.secret,
        lifetime_seconds=settings.jwt_token_lifetime,
    )


auth_backend = AuthenticationBackend(
    name=Constants.JWT_AUTH_BACKEND_NAME,
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:
        if len(password) < settings.user_password_min_len:
            raise InvalidPasswordException(
                reason=Messages.PASSWORD_TOO_SHORT,
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason=Messages.EMAIL_IN_PASSWORD
            )

    async def on_after_register(
            self, user: User, request: Optional[Request] = None
    ):
        logging.info(f'{Messages.USER_REGISTERED}{user.email}')


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(
    active=True
)
current_superuser = fastapi_users.current_user(
    active=True,
    superuser=True
)


async def current_driver(user: User = Depends(current_user)) -> User:
    '''Зависимость для получения текущего пользователя-водителя'''
    if not user.is_driver:
        raise HTTPException(
            status_code=403,
            detail='Недостаточно прав. Требуется роль водителя.'
        )
    return user


async def current_assistant(user: User = Depends(current_user)) -> User:
    '''Зависимость для получения текущего пользователя-ассистента'''
    if not user.is_assistant:
        raise HTTPException(
            status_code=403,
            detail='Недостаточно прав. Требуется роль ассистента.'
        )
    return user


async def current_administrator(user: User = Depends(current_user)) -> User:
    '''Зависимость для получения текущего пользователя-администратора'''
    if not user.is_administrator:
        raise HTTPException(
            status_code=403,
            detail='Недостаточно прав. Требуется роль администратора.'
        )
    return user
