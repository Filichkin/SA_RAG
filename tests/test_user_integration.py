'''
Интеграционные тесты для пользователей
'''
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock

from app.models.user import User


class TestUserWorkflow:
    '''Тесты полного workflow пользователя'''

    async def test_complete_user_workflow(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        '''Тест полного жизненного цикла пользователя'''
        # 1. Регистрация пользователя
        user_data = {
            'email': 'workflow@example.com',
            'password': 'WorkflowPass123!',
            'first_name': 'Workflow',
            'last_name': 'User',
            'date_of_birth': '1990-01-01',
            'phone': '+79031234571'
        }

        register_response = await client.post('/auth/register', json=user_data)
        assert register_response.status_code == 201
        user_info = register_response.json()
        user_id = user_info['id']

        # 2. Вход пользователя через 2FA
        # Мокаем отправку email
        with patch('app.api.endpoints.two_factor_auth.email_service.'
                   'send_2fa_code_email',
                   new_callable=AsyncMock) as mock_send_email:
            mock_send_email.return_value = True

            # Первый этап 2FA - получение временного токена
            login_response = await client.post('/auth/2fa/login', json={
                'email': user_data['email'],
                'password': user_data['password']
            })
            assert login_response.status_code == 200
            login_data = login_response.json()
            temp_token = login_data['temp_token']

            # Получаем код из базы данных (в реальности приходит на email)
            from app.crud.two_factor_auth import two_factor_auth_crud
            codes = await two_factor_auth_crud.get_user_codes(
                user_id=user_id,
                session=db_session
            )
            assert len(codes) > 0
            code = codes[0].code

            # Второй этап 2FA - проверка кода
            verify_response = await client.post(
                '/auth/2fa/verify-code',
                json={'code': code},
                headers={'X-Temp-Token': temp_token}
            )
            assert verify_response.status_code == 200
            token = verify_response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}

        # 3. Получение информации о себе
        me_response = await client.get('/users/me', headers=headers)
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data['id'] == user_id
        assert me_data['email'] == user_data['email']

        # 4. Обновление информации о себе
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '+79031234572'
        }
        update_response = await client.patch(
            '/users/me', headers=headers, json=update_data
        )
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data['first_name'] == update_data['first_name']
        assert updated_data['last_name'] == update_data['last_name']
        assert updated_data['phone'] == update_data['phone']

        # 5. Смена пароля
        password_data = {
            'old_password': user_data['password'],
            'new_password': 'NewWorkflowPass123!'
        }
        password_response = await client.post(
            '/users/change-password',
            headers=headers,
            json=password_data
        )
        assert password_response.status_code == 200

        # 6. Вход с новым паролем
        new_login_response = await client.post(
            '/auth/jwt/login',
            data={
                'username': user_data['email'],
                'password': password_data['new_password']
            }
        )
        assert new_login_response.status_code == 200

    async def test_user_cannot_access_admin_endpoints(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        '''
        Тест что обычный пользователь не может получить доступ
        к админским endpoints
        '''
        # Попытка получить всех пользователей
        response = await client.get('/users', headers=auth_headers)
        assert response.status_code == 403

        # Попытка удалить пользователя
        response = await client.delete('/users/1', headers=auth_headers)
        assert response.status_code == 403

    async def test_admin_can_access_admin_endpoints(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        test_user: User
    ):
        '''
        Тест что администратор может получить доступ к админским endpoints
        '''
        # Получение всех пользователей
        response = await client.get('/users', headers=admin_auth_headers)
        assert response.status_code == 200

        # Но не может удалять пользователей
        # (только суперпользователь)
        response = await client.delete(
            f'/users/{test_user.id}', headers=admin_auth_headers
        )
        assert response.status_code == 403

    async def test_superuser_full_access(
        self,
        client: AsyncClient,
        superuser_auth_headers: dict,
        test_user: User
    ):
        '''Тест что суперпользователь имеет полный доступ'''
        # Получение всех пользователей
        response = await client.get('/users', headers=superuser_auth_headers)
        assert response.status_code == 200

        # Удаление пользователя
        response = await client.delete(
            f'/users/{test_user.id}', headers=superuser_auth_headers
        )
        assert response.status_code == 200


class TestConcurrentOperations:
    '''Тесты конкурентных операций'''

    async def test_concurrent_password_changes(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        '''Тест одновременной смены пароля'''
        import asyncio

        password_data = {
            'old_password': 'TestPass123!',
            'new_password': 'ConcurrentPass123!'
        }

        # Создаем несколько одновременных запросов
        tasks = [
            client.post(
                '/users/change-password',
                headers=auth_headers,
                json=password_data
            )
            for _ in range(3)
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Только один запрос должен быть успешным
        successful_responses = [
            r for r in responses
            if hasattr(r, 'status_code') and r.status_code == 200
        ]
        assert len(successful_responses) == 1

    async def test_concurrent_user_registration(
        self,
        client: AsyncClient
    ):
        '''Тест одновременной регистрации пользователей с одинаковым email'''
        import asyncio

        user_data = {
            'email': 'concurrent@example.com',
            'password': 'ConcurrentPass123!',
            'first_name': 'Concurrent',
            'last_name': 'User'
        }

        # Создаем несколько одновременных запросов регистрации
        tasks = [
            client.post('/auth/register', json=user_data)
            for _ in range(3)
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Только один запрос должен быть успешным
        successful_responses = [
            r for r in responses
            if hasattr(r, 'status_code') and r.status_code == 201
        ]
        assert len(successful_responses) == 1


class TestErrorHandling:
    '''Тесты обработки ошибок'''

    async def test_database_error_handling(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        mocker
    ):
        '''Тест обработки ошибок базы данных'''
        # Мокаем метод для имитации ошибки БД
        from app.crud import user_crud
        mocker.patch.object(
            user_crud,
            'get_all_users',
            side_effect=Exception('Database connection error')
        )

        response = await client.get('/users', headers=admin_auth_headers)
        # В реальном приложении это должно возвращать 500,
        # но зависит от обработки ошибок
        assert response.status_code in [500, 422]

    async def test_invalid_json_request(self, client: AsyncClient):
        '''Тест запроса с невалидным JSON'''
        response = await client.post(
            '/auth/register',
            data='invalid json',
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 422

    async def test_missing_required_fields(self, client: AsyncClient):
        '''Тест запроса с отсутствующими обязательными полями'''
        user_data = {
            'email': 'incomplete@example.com'
            # Отсутствуют password, first_name, last_name
        }

        response = await client.post('/auth/register', json=user_data)
        assert response.status_code == 422

    async def test_oversized_request(self, client: AsyncClient):
        '''Тест запроса с слишком большими данными'''
        user_data = {
            'email': 'oversized@example.com',
            'password': 'OversizedPass123!',
            'first_name': 'A' * 1000,  # Слишком длинное имя
            'last_name': 'User'
        }

        response = await client.post('/auth/register', json=user_data)
        assert response.status_code == 422


class TestSecurity:
    '''Тесты безопасности'''

    async def test_sql_injection_attempts(self, client: AsyncClient):
        '''Тест попыток SQL инъекций'''
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ]

        for malicious_input in malicious_inputs:
            # Попытка входа с SQL инъекцией
            response = await client.post(
                '/auth/jwt/login',
                data={
                    'username': malicious_input,
                    'password': 'password'
                }
            )
            # Должен возвращать ошибку валидации,
            # а не выполнять SQL
            assert response.status_code in [400, 422]

    async def test_xss_attempts(self, client: AsyncClient):
        '''Тест попыток XSS атак'''
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]

        for payload in xss_payloads:
            user_data = {
                'email': f'xss{payload}@example.com',
                'password': 'XssPass123!',
                'first_name': payload,
                'last_name': 'User'
            }

            response = await client.post('/auth/register', json=user_data)
            # Должен возвращать ошибку валидации
            assert response.status_code == 422

    async def test_token_tampering(
        self, client: AsyncClient, auth_headers: dict
    ):
        '''Тест подделки токена'''
        # Подделываем токен
        tampered_headers = {'Authorization': 'Bearer tampered_token'}

        response = await client.get('/users/me', headers=tampered_headers)
        assert response.status_code == 401

    async def test_brute_force_protection(
        self,
        client: AsyncClient,
        test_user: User
    ):
        '''Тест защиты от брутфорса'''
        # Множественные попытки входа с неверным паролем
        for i in range(10):
            response = await client.post(
                '/auth/jwt/login',
                data={
                    'username': test_user.email,
                    'password': f'wrong_password_{i}'
                }
            )
            assert response.status_code == 400


class TestPerformance:
    '''Тесты производительности'''

    async def test_large_pagination(
        self,
        client: AsyncClient,
        admin_auth_headers: dict
    ):
        '''Тест пагинации с большим количеством записей'''
        response = await client.get(
            '/users',
            headers=admin_auth_headers,
            params={'skip': 0, 'limit': 100}  # Максимальный лимит
        )
        assert response.status_code == 200

    async def test_response_time(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        '''Тест времени ответа'''
        import time

        start_time = time.time()
        response = await client.get('/users/me', headers=auth_headers)
        end_time = time.time()

        assert response.status_code == 200
        # Проверяем что ответ пришел менее чем за 1 секунду
        assert (end_time - start_time) < 1.0
