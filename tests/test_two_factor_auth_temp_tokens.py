'''
Тесты для двухфакторной аутентификации с временными токенами
'''
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock

from app.core.user import get_jwt_strategy
from app.crud.two_factor_auth import two_factor_auth_crud
from app.models.user import User


class TestTwoFactorAuthTempTokens:
    '''Тесты для временных токенов в 2FA'''

    @pytest.mark.asyncio
    async def test_two_factor_auth_login_returns_temp_token(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        '''Тест что two_factor_auth_login возвращает временный токен'''
        # Мокаем отправку email
        with patch('app.api.endpoints.two_factor_auth.email_service.'
                   'send_2fa_code_email',
                   new_callable=AsyncMock) as mock_send_email:
            mock_send_email.return_value = True

            login_data = {
            'email': test_user.email,
            'password': 'TestPass123!'
            }

            response = await client.post('/auth/2fa/login', json=login_data)

            assert response.status_code == 200
            data = response.json()

            # Проверяем что возвращается сообщение и временный токен
            assert 'message' in data
            assert 'temp_token' in data
            assert data['temp_token'] is not None
            assert len(data['temp_token']) > 0

    @pytest.mark.asyncio
    async def test_temp_token_validation(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        '''Тест валидации временного токена'''
        # Создаем временный токен
        jwt_strategy = get_jwt_strategy()
        temp_token = jwt_strategy.write_temp_token(test_user.id)

        # Проверяем что токен валиден
        user_id = await jwt_strategy.read_temp_token(temp_token)
        assert user_id == test_user.id

        # Проверяем что невалидный токен возвращает None
        invalid_user_id = await jwt_strategy.read_temp_token('invalid_token')
        assert invalid_user_id is None

    @pytest.mark.asyncio
    async def test_two_factor_auth_verify_code_with_temp_token(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        '''Тест проверки кода с временным токеном'''
        # Создаем временный токен
        jwt_strategy = get_jwt_strategy()
        temp_token = jwt_strategy.write_temp_token(test_user.id)

        # Создаем 2FA код в базе данных
        test_code = '123456'
        await two_factor_auth_crud.create_code(
            user_id=test_user.id,
            code=test_code,
            session=db_session
        )

        # Тестируем проверку кода с временным токеном
        verify_data = {'code': test_code}
        headers = {'X-Temp-Token': temp_token}

        response = await client.post(
            '/auth/2fa/verify-code',
            json=verify_data,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Проверяем что возвращается JWT токен
        assert 'access_token' in data
        assert 'token_type' in data
        assert data['token_type'] == 'bearer'
        assert len(data['access_token']) > 0

    @pytest.mark.asyncio
    async def test_two_factor_auth_verify_code_invalid_temp_token(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        '''Тест проверки кода с невалидным временным токеном'''
        verify_data = {'code': '123456'}
        headers = {'X-Temp-Token': 'invalid_token'}

        response = await client.post(
            '/auth/2fa/verify-code',
            json=verify_data,
            headers=headers
        )

        assert response.status_code == 401
        data = response.json()
        assert 'detail' in data
        assert ('недействительный' in data['detail'].lower() or
                'invalid' in data['detail'].lower())

    @pytest.mark.asyncio
    async def test_two_factor_auth_verify_code_missing_temp_token(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        '''Тест проверки кода без временного токена'''
        verify_data = {'code': '123456'}

        response = await client.post(
            '/auth/2fa/verify-code',
            json=verify_data
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_two_factor_auth_verify_code_invalid_code(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        '''Тест проверки кода с неверным кодом'''
        # Создаем временный токен
        jwt_strategy = get_jwt_strategy()
        temp_token = jwt_strategy.write_temp_token(test_user.id)

        # Создаем 2FA код в базе данных
        test_code = '123456'
        await two_factor_auth_crud.create_code(
            user_id=test_user.id,
            code=test_code,
            session=db_session
        )

        # Тестируем с неверным кодом
        verify_data = {'code': '654321'}  # Неверный код
        headers = {'X-Temp-Token': temp_token}

        response = await client.post(
            '/auth/2fa/verify-code',
            json=verify_data,
            headers=headers
        )

        assert response.status_code == 400
        data = response.json()
        assert 'detail' in data

    @pytest.mark.asyncio
    async def test_temp_token_expiration(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        '''Тест истечения срока действия временного токена'''
        # Создаем временный токен с очень коротким сроком жизни
        jwt_strategy = get_jwt_strategy()

        # Мокаем время истечения токена
        with patch('app.core.user.generate_jwt') as mock_generate_jwt:
            # Создаем токен который уже истек
            import jwt
            from app.core.config import settings

            expired_payload = {
                'sub': str(test_user['id']),
                'type': 'temp_2fa',
                'aud': ['fastapi-users:auth'],
                'exp': 0  # Истекший токен
            }

            expired_token = jwt.encode(
                expired_payload,
                settings.secret,
                algorithm='HS256'
            )

            mock_generate_jwt.return_value = expired_token

            # Проверяем что истекший токен не валиден
            user_id = await jwt_strategy.read_temp_token(expired_token)
            assert user_id is None

    @pytest.mark.asyncio
    async def test_complete_2fa_workflow_with_temp_token(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        '''Тест полного workflow 2FA с временным токеном'''
        # Мокаем отправку email
        with patch('app.api.endpoints.two_factor_auth.email_service.'
                   'send_2fa_code_email',
                   new_callable=AsyncMock) as mock_send_email:
            mock_send_email.return_value = True

            # 1. Первый этап - получение временного токена
            login_data = {
            'email': test_user.email,
            'password': 'TestPass123!'
            }

            login_response = await client.post(
                '/auth/2fa/login',
                json=login_data
                )
            assert login_response.status_code == 200

            login_data = login_response.json()
            temp_token = login_data['temp_token']

            # 2. Получаем код из базы данных (в реальности приходит на email)
            codes = await two_factor_auth_crud.get_user_codes(
                user_id=test_user.id,
                session=db_session
            )
            assert len(codes) > 0
            code = codes[0].code

            # 3. Второй этап - проверка кода с временным токеном
            verify_data = {'code': code}
            headers = {'X-Temp-Token': temp_token}

            verify_response = await client.post(
                '/auth/2fa/verify-code',
                json=verify_data,
                headers=headers
            )

            assert verify_response.status_code == 200
            verify_data = verify_response.json()

            # 4. Проверяем что полученный JWT токен работает
            jwt_token = verify_data['access_token']
            jwt_headers = {'Authorization': f'Bearer {jwt_token}'}

            me_response = await client.get('/users/me', headers=jwt_headers)
            assert me_response.status_code == 200

            me_data = me_response.json()
            assert me_data['id'] == test_user.id
            assert me_data['email'] == test_user.email
