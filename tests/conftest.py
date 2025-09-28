'''
Конфигурация для тестов
'''
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.db import get_async_session, Base
from app.models.user import User
from app.core.user import get_user_manager
from app.schemas.user import UserCreate


# Тестовая база данных
SQLALCHEMY_DATABASE_URL = 'sqlite+aiosqlite:///./test.db'

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_async_session() -> AsyncGenerator[
    AsyncSession, None
]:
    '''Переопределение сессии для тестов'''
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    '''Создание event loop для тестов'''
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='function')
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    '''Создание тестовой сессии базы данных'''
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            yield session
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope='function')
async def client(db_session: AsyncSession) -> AsyncGenerator[
    AsyncClient, None
]:
    '''Создание тестового клиента'''
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    '''Создание тестового пользователя'''
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

    user_db = SQLAlchemyUserDatabase(db_session, User)
    async for user_manager in get_user_manager(user_db):
        user_create = UserCreate(
            email='test@example.com',
            password='TestPass123!',
            password_confirm='TestPass123!',
            first_name='Test',
            last_name='User',
            date_of_birth=None,
            phone='+79031234567'
        )

        user = await user_manager.create(user_create)
        return user


@pytest_asyncio.fixture
async def test_admin_user(db_session: AsyncSession) -> User:
    '''Создание тестового администратора'''
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

    user_db = SQLAlchemyUserDatabase(db_session, User)
    async for user_manager in get_user_manager(user_db):
        user_create = UserCreate(
            email='admin@example.com',
            password='AdminPass123!',
            password_confirm='AdminPass123!',
            first_name='Admin',
            last_name='User',
            date_of_birth=None,
            phone='+79031234568'
        )

        user = await user_manager.create(user_create)
        # Устанавливаем роль администратора
        user.is_administrator = True
        await db_session.commit()
        await db_session.refresh(user)
        return user


@pytest_asyncio.fixture
async def test_superuser(db_session: AsyncSession) -> User:
    '''Создание тестового суперпользователя'''
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

    user_db = SQLAlchemyUserDatabase(db_session, User)
    async for user_manager in get_user_manager(user_db):
        user_create = UserCreate(
            email='superuser@example.com',
            password='SuperPass123!',
            password_confirm='SuperPass123!',
            first_name='Super',
            last_name='User',
            date_of_birth=None,
            phone='+79031234569'
        )

        user = await user_manager.create(user_create)
        # Устанавливаем роль суперпользователя
        user.is_superuser = True
        await db_session.commit()
        await db_session.refresh(user)
        return user


@pytest_asyncio.fixture
async def auth_headers(
    client: AsyncClient, test_user: User, db_session: AsyncSession
) -> dict:
    '''Получение заголовков авторизации для тестового пользователя'''
    from unittest.mock import patch, AsyncMock

    # Мокаем отправку email
    with patch('app.api.endpoints.two_factor_auth.email_service.'
               'send_2fa_code_email',
               new_callable=AsyncMock) as mock_send_email:
        mock_send_email.return_value = True

        # Первый этап 2FA
        login_response = await client.post('/auth/2fa/login', json={
            'email': test_user.email,
            'password': 'TestPass123!'
        })
        assert login_response.status_code == 200
        temp_token = login_response.json()['temp_token']

        # Получаем код из базы данных
        from app.crud.two_factor_auth import two_factor_auth_crud
        codes = await two_factor_auth_crud.get_user_codes(
            user_id=test_user.id,
            session=db_session
        )
        assert len(codes) > 0
        code = codes[0].code

        # Второй этап 2FA
        verify_response = await client.post(
            '/auth/2fa/verify-code',
            json={'code': code},
            headers={'X-Temp-Token': temp_token}
        )
        assert verify_response.status_code == 200
        token = verify_response.json()['access_token']
        return {'Authorization': f'Bearer {token}'}


@pytest_asyncio.fixture
async def admin_auth_headers(
    client: AsyncClient, test_admin_user: User, db_session: AsyncSession
) -> dict:
    '''Получение заголовков авторизации для администратора'''
    from unittest.mock import patch, AsyncMock

    # Мокаем отправку email
    with patch('app.api.endpoints.two_factor_auth.email_service.'
               'send_2fa_code_email',
               new_callable=AsyncMock) as mock_send_email:
        mock_send_email.return_value = True

        # Первый этап 2FA
        login_response = await client.post('/auth/2fa/login', json={
            'email': test_admin_user.email,
            'password': 'AdminPass123!'
        })
        assert login_response.status_code == 200
        temp_token = login_response.json()['temp_token']

        # Получаем код из базы данных
        from app.crud.two_factor_auth import two_factor_auth_crud
        codes = await two_factor_auth_crud.get_user_codes(
            user_id=test_admin_user.id,
            session=db_session
        )
        assert len(codes) > 0
        code = codes[0].code

        # Второй этап 2FA
        verify_response = await client.post(
            '/auth/2fa/verify-code',
            json={'code': code},
            headers={'X-Temp-Token': temp_token}
        )
        assert verify_response.status_code == 200
        token = verify_response.json()['access_token']
        return {'Authorization': f'Bearer {token}'}


@pytest_asyncio.fixture
async def superuser_auth_headers(
    client: AsyncClient, test_superuser: User, db_session: AsyncSession
) -> dict:
    '''Получение заголовков авторизации для суперпользователя'''
    from unittest.mock import patch, AsyncMock

    # Мокаем отправку email
    with patch('app.api.endpoints.two_factor_auth.email_service.'
               'send_2fa_code_email',
               new_callable=AsyncMock) as mock_send_email:
        mock_send_email.return_value = True

        # Первый этап 2FA
        login_response = await client.post('/auth/2fa/login', json={
            'email': test_superuser.email,
            'password': 'SuperPass123!'
        })
        assert login_response.status_code == 200
        temp_token = login_response.json()['temp_token']

        # Получаем код из базы данных
        from app.crud.two_factor_auth import two_factor_auth_crud
        codes = await two_factor_auth_crud.get_user_codes(
            user_id=test_superuser.id,
            session=db_session
        )
        assert len(codes) > 0
        code = codes[0].code

        # Второй этап 2FA
        verify_response = await client.post(
            '/auth/2fa/verify-code',
            json={'code': code},
            headers={'X-Temp-Token': temp_token}
        )
        assert verify_response.status_code == 200
        token = verify_response.json()['access_token']
        return {'Authorization': f'Bearer {token}'}
