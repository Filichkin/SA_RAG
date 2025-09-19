'''
Примеры использования тестов
'''
import pytest
from httpx import AsyncClient

from tests.test_utils import TestDataFactory, TestConstants


class TestExamples:
    '''Примеры различных типов тестов'''

    async def test_simple_endpoint_example(self, client: AsyncClient):
        '''Пример простого теста endpoint'''
        # Создаем тестовые данные
        user_data = TestDataFactory.create_user_data()

        # Выполняем запрос
        response = await client.post('/auth/register', json=user_data)

        # Проверяем результат
        assert response.status_code == TestConstants.CREATED
        assert 'id' in response.json()

    async def test_authenticated_endpoint_example(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        '''Пример теста с аутентификацией'''
        response = await client.get('/users/me', headers=auth_headers)

        assert response.status_code == TestConstants.OK
        user_data = response.json()
        assert 'email' in user_data
        assert 'first_name' in user_data

    async def test_admin_endpoint_example(
        self,
        client: AsyncClient,
        admin_auth_headers: dict
    ):
        '''Пример теста админского endpoint'''
        response = await client.get('/users', headers=admin_auth_headers)

        assert response.status_code == TestConstants.OK
        users = response.json()
        assert isinstance(users, list)

    async def test_validation_example(self):
        '''Пример теста валидации'''
        from app.schemas.user import UserCreate

        # Валидные данные
        valid_data = TestDataFactory.create_user_data()
        user = UserCreate(**valid_data)
        assert user.email == valid_data['email']

        # Невалидные данные
        invalid_data = TestDataFactory.create_invalid_user_data()
        with pytest.raises(ValueError):
            UserCreate(**invalid_data)

    async def test_error_handling_example(self, client: AsyncClient):
        '''Пример теста обработки ошибок'''
        # Попытка доступа без авторизации
        response = await client.get('/users/me')
        assert response.status_code == TestConstants.UNAUTHORIZED

        # Попытка доступа к несуществующему ресурсу
        response = await client.get('/users/99999')
        assert response.status_code == TestConstants.NOT_FOUND

    async def test_pagination_example(
        self,
        client: AsyncClient,
        admin_auth_headers: dict
    ):
        '''Пример теста пагинации'''
        # Тест с параметрами пагинации
        response = await client.get(
            '/users',
            headers=admin_auth_headers,
            params={'skip': 0, 'limit': 5}
        )

        assert response.status_code == TestConstants.OK
        users = response.json()
        assert len(users) <= 5

    async def test_concurrent_operations_example(self, client: AsyncClient):
        '''Пример теста конкурентных операций'''
        import asyncio

        # Создаем несколько одновременных запросов
        user_data = TestDataFactory.create_user_data()

        tasks = [
            client.post('/auth/register', json=user_data)
            for _ in range(3)
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Только один должен быть успешным
        successful = [
            r for r in responses
            if hasattr(r, 'status_code') and r.status_code == 201
        ]
        assert len(successful) == 1

    async def test_security_example(self, client: AsyncClient):
        '''Пример теста безопасности'''
        # Попытка SQL инъекции
        malicious_input = "'; DROP TABLE users; --"

        response = await client.post(
            '/auth/jwt/login',
            data={
                'username': malicious_input,
                'password': 'password'
            }
        )

        # Должен возвращать ошибку валидации
        assert response.status_code in [400, 422]

    async def test_performance_example(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        '''Пример теста производительности'''
        import time

        start_time = time.time()
        response = await client.get('/users/me', headers=auth_headers)
        end_time = time.time()

        assert response.status_code == TestConstants.OK
        assert (end_time - start_time) < 1.0  # Менее 1 секунды

    @pytest.mark.parametrize('email,expected_status', [
        ('valid@example.com', 201),
        ('invalid-email', 422),
        ('', 422),
        ('test@', 422),
    ])
    async def test_parametrized_example(
        self,
        client: AsyncClient,
        email: str,
        expected_status: int
    ):
        '''Пример параметризованного теста'''
        user_data = TestDataFactory.create_user_data(email=email)

        response = await client.post('/auth/register', json=user_data)
        assert response.status_code == expected_status

    async def test_fixture_usage_example(
        self,
        client: AsyncClient,
        test_user,
        auth_headers: dict
    ):
        '''Пример использования фикстур'''
        # test_user создан автоматически
        assert test_user.email is not None
        assert test_user.id is not None

        # auth_headers настроены для test_user
        response = await client.get('/users/me', headers=auth_headers)
        assert response.status_code == TestConstants.OK

        user_data = response.json()
        assert user_data['id'] == test_user.id
        assert user_data['email'] == test_user.email

    async def test_mock_example(self, client: AsyncClient, mocker):
        '''Пример использования моков'''
        # Мокаем метод для имитации ошибки
        from app.crud import user_crud
        mocker.patch.object(
            user_crud,
            'get_user_by_id',
            side_effect=Exception('Database error')
        )

        # Теперь запрос должен вызвать ошибку
        response = await client.get('/users/1')
        assert response.status_code in [500, 422]

    async def test_database_transaction_example(
        self,
        client: AsyncClient,
        db_session
    ):
        '''Пример теста с транзакциями базы данных'''
        # Создаем пользователя
        user_data = TestDataFactory.create_user_data()
        response = await client.post('/auth/register', json=user_data)
        assert response.status_code == TestConstants.CREATED

        # Проверяем что пользователь создан в БД
        from app.models.user import User
        from sqlalchemy import select

        result = await db_session.execute(
            select(User).where(User.email == user_data['email'])
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == user_data['email']
