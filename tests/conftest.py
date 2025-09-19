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
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    '''Создание тестового пользователя'''
    user_manager = get_user_manager()

    user_create = UserCreate(
        email='test@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='User',
        date_of_birth=None,
        phone='+79031234567'
    )

    user = await user_manager.create(user_create, db_session)
    return user


@pytest_asyncio.fixture
async def test_admin_user(db_session: AsyncSession) -> User:
    '''Создание тестового администратора'''
    user_manager = get_user_manager()

    user_create = UserCreate(
        email='admin@example.com',
        password='AdminPass123!',
        first_name='Admin',
        last_name='User',
        date_of_birth=None,
        phone='+79031234568'
    )

    user = await user_manager.create(user_create, db_session)
    # Устанавливаем роль администратора
    user.is_administrator = True
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_superuser(db_session: AsyncSession) -> User:
    '''Создание тестового суперпользователя'''
    user_manager = get_user_manager()

    user_create = UserCreate(
        email='superuser@example.com',
        password='SuperPass123!',
        first_name='Super',
        last_name='User',
        date_of_birth=None,
        phone='+79031234569'
    )

    user = await user_manager.create(user_create, db_session)
    # Устанавливаем роль суперпользователя
    user.is_superuser = True
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(
    client: AsyncClient, test_user: User
) -> dict:
    '''Получение заголовков авторизации для тестового пользователя'''
    response = await client.post(
        '/auth/jwt/login',
        data={
            'username': test_user.email,
            'password': 'TestPass123!'
        }
    )
    assert response.status_code == 200
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest_asyncio.fixture
async def admin_auth_headers(
    client: AsyncClient, test_admin_user: User
) -> dict:
    '''Получение заголовков авторизации для администратора'''
    response = await client.post(
        '/auth/jwt/login',
        data={
            'username': test_admin_user.email,
            'password': 'AdminPass123!'
        }
    )
    assert response.status_code == 200
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest_asyncio.fixture
async def superuser_auth_headers(
    client: AsyncClient, test_superuser: User
) -> dict:
    '''Получение заголовков авторизации для суперпользователя'''
    response = await client.post(
        '/auth/jwt/login',
        data={
            'username': test_superuser.email,
            'password': 'SuperPass123!'
        }
    )
    assert response.status_code == 200
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}
