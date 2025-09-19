'''
Тесты для endpoints пользователей
'''
from httpx import AsyncClient

from app.models.user import User
from app.core.constants import Messages


class TestGetAllUsers:
    '''Тесты для получения всех пользователей'''

    async def test_get_all_users_success_admin(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        test_user: User,
        test_admin_user: User
    ):
        '''Тест успешного получения всех пользователей администратором'''
        response = await client.get(
            '/users',
            headers=admin_auth_headers,
            params={'skip': 0, 'limit': 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # test_user и test_admin_user
        assert len(data) >= 2

        # Проверяем, что в ответе есть нужные поля
        user_data = data[0]
        assert 'id' in user_data
        assert 'email' in user_data
        assert 'first_name' in user_data
        assert 'last_name' in user_data

    async def test_get_all_users_success_superuser(
        self,
        client: AsyncClient,
        superuser_auth_headers: dict,
        test_user: User,
        test_superuser: User
    ):
        '''Тест успешного получения всех пользователей суперпользователем'''
        response = await client.get(
            '/users',
            headers=superuser_auth_headers,
            params={'skip': 0, 'limit': 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_all_users_forbidden_regular_user(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        '''Тест запрета доступа для обычного пользователя'''
        response = await client.get(
            '/users',
            headers=auth_headers,
            params={'skip': 0, 'limit': 10}
        )

        assert response.status_code == 403
        detail = Messages.INSUFFICIENT_PERMISSIONS_MSG
        assert response.json()['detail'] == detail

    async def test_get_all_users_unauthorized(self, client: AsyncClient):
        '''Тест доступа без авторизации'''
        response = await client.get(
            '/users',
            params={'skip': 0, 'limit': 10}
        )

        assert response.status_code == 401

    async def test_get_all_users_pagination(
        self,
        client: AsyncClient,
        admin_auth_headers: dict
    ):
        '''Тест пагинации'''
        response = await client.get(
            '/users',
            headers=admin_auth_headers,
            params={'skip': 0, 'limit': 1}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1

    async def test_get_all_users_invalid_pagination(
        self,
        client: AsyncClient,
        admin_auth_headers: dict
    ):
        '''Тест невалидных параметров пагинации'''
        # Отрицательный skip
        response = await client.get(
            '/users',
            headers=admin_auth_headers,
            params={'skip': -1, 'limit': 10}
        )
        assert response.status_code == 422

        # Слишком большой limit
        response = await client.get(
            '/users',
            headers=admin_auth_headers,
            params={'skip': 0, 'limit': 1000}
        )
        assert response.status_code == 422

        # Нулевой limit
        response = await client.get(
            '/users',
            headers=admin_auth_headers,
            params={'skip': 0, 'limit': 0}
        )
        assert response.status_code == 422


class TestDeleteUser:
    '''Тесты для удаления пользователя'''

    async def test_delete_user_success_superuser(
        self,
        client: AsyncClient,
        superuser_auth_headers: dict,
        test_user: User,
        test_superuser: User
    ):
        '''Тест успешного удаления пользователя суперпользователем'''
        response = await client.delete(
            f'/users/{test_user.id}',
            headers=superuser_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == test_user.id
        assert data['email'] == test_user.email

    async def test_delete_user_forbidden_admin(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        test_user: User
    ):
        '''Тест запрета удаления пользователя администратором'''
        response = await client.delete(
            f'/users/{test_user.id}',
            headers=admin_auth_headers
        )

        assert response.status_code == 403

    async def test_delete_user_forbidden_regular_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        '''Тест запрета удаления пользователя обычным пользователем'''
        response = await client.delete(
            f'/users/{test_user.id}',
            headers=auth_headers
        )

        assert response.status_code == 403

    async def test_delete_user_unauthorized(
        self, client: AsyncClient, test_user: User
    ):
        '''Тест удаления пользователя без авторизации'''
        response = await client.delete(f'/users/{test_user.id}')
        assert response.status_code == 401

    async def test_delete_user_not_found(
        self,
        client: AsyncClient,
        superuser_auth_headers: dict
    ):
        '''Тест удаления несуществующего пользователя'''
        response = await client.delete(
            '/users/99999',
            headers=superuser_auth_headers
        )

        assert response.status_code == 404
        assert response.json()['detail'] == Messages.USER_NOT_FOUND_MSG

    async def test_delete_user_self(
        self,
        client: AsyncClient,
        superuser_auth_headers: dict,
        test_superuser: User
    ):
        '''Тест попытки удаления самого себя'''
        response = await client.delete(
            f'/users/{test_superuser.id}',
            headers=superuser_auth_headers
        )

        assert response.status_code == 400
        assert response.json()['detail'] == Messages.CANNOT_DELETE_SELF_MSG


class TestChangePassword:
    '''Тесты для смены пароля'''

    async def test_change_password_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        '''Тест успешной смены пароля'''
        password_data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewTestPass123!'
        }

        response = await client.post(
            '/users/change-password',
            headers=auth_headers,
            json=password_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data['message'] == Messages.PASSWORD_CHANGED_SUCCESS_MSG
        assert 'access_token' in data
        assert data['token_type'] == 'bearer'

    async def test_change_password_wrong_old_password(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        '''Тест смены пароля с неверным старым паролем'''
        password_data = {
            'old_password': 'WrongPassword123!',
            'new_password': 'NewTestPass123!'
        }

        response = await client.post(
            '/users/change-password',
            headers=auth_headers,
            json=password_data
        )

        assert response.status_code == 400
        detail = Messages.INVALID_OLD_PASSWORD_MSG
        assert response.json()['detail'] == detail

    async def test_change_password_same_password(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        '''Тест смены пароля на тот же пароль'''
        password_data = {
            'old_password': 'TestPass123!',
            'new_password': 'TestPass123!'
        }

        response = await client.post(
            '/users/change-password',
            headers=auth_headers,
            json=password_data
        )

        assert response.status_code == 422

    async def test_change_password_weak_password(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        '''Тест смены пароля на слабый пароль'''
        password_data = {
            'old_password': 'TestPass123!',
            'new_password': '123'
        }

        response = await client.post(
            '/users/change-password',
            headers=auth_headers,
            json=password_data
        )

        assert response.status_code == 422

    async def test_change_password_unauthorized(self, client: AsyncClient):
        '''Тест смены пароля без авторизации'''
        password_data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewTestPass123!'
        }

        response = await client.post(
            '/users/change-password',
            json=password_data
        )

        assert response.status_code == 401

    async def test_change_password_invalid_data(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        '''Тест смены пароля с невалидными данными'''
        # Отсутствует old_password
        password_data = {
            'new_password': 'NewTestPass123!'
        }

        response = await client.post(
            '/users/change-password',
            headers=auth_headers,
            json=password_data
        )

        assert response.status_code == 422

        # Отсутствует new_password
        password_data = {
            'old_password': 'TestPass123!'
        }

        response = await client.post(
            '/users/change-password',
            headers=auth_headers,
            json=password_data
        )

        assert response.status_code == 422


class TestUserRegistration:
    '''Тесты для регистрации пользователей'''

    async def test_register_user_success(self, client: AsyncClient):
        '''Тест успешной регистрации пользователя'''
        user_data = {
            'email': 'newuser@example.com',
            'password': 'NewUserPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'date_of_birth': '1990-01-01',
            'phone': '+79031234570'
        }

        response = await client.post('/auth/register', json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data['email'] == user_data['email']
        assert data['first_name'] == user_data['first_name']
        assert data['last_name'] == user_data['last_name']
        assert 'id' in data

    async def test_register_user_duplicate_email(
        self,
        client: AsyncClient,
        test_user: User
    ):
        '''Тест регистрации с существующим email'''
        user_data = {
            'email': test_user.email,  # Используем существующий email
            'password': 'NewUserPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = await client.post('/auth/register', json=user_data)
        assert response.status_code == 400

    async def test_register_user_invalid_email(self, client: AsyncClient):
        '''Тест регистрации с невалидным email'''
        user_data = {
            'email': 'invalid-email',
            'password': 'NewUserPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = await client.post('/auth/register', json=user_data)
        assert response.status_code == 422

    async def test_register_user_weak_password(self, client: AsyncClient):
        '''Тест регистрации со слабым паролем'''
        user_data = {
            'email': 'weakpass@example.com',
            'password': '123',  # Слабый пароль
            'first_name': 'New',
            'last_name': 'User'
        }

        response = await client.post('/auth/register', json=user_data)
        assert response.status_code == 422

    async def test_register_user_invalid_phone(self, client: AsyncClient):
        '''Тест регистрации с невалидным телефоном'''
        user_data = {
            'email': 'invalidphone@example.com',
            'password': 'NewUserPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '123'  # Невалидный телефон
        }

        response = await client.post('/auth/register', json=user_data)
        assert response.status_code == 422

    async def test_register_user_future_birth_date(self, client: AsyncClient):
        '''Тест регистрации с датой рождения в будущем'''
        user_data = {
            'email': 'futurebirth@example.com',
            'password': 'NewUserPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'date_of_birth': '2030-01-01'  # Дата в будущем
        }

        response = await client.post('/auth/register', json=user_data)
        assert response.status_code == 422


class TestUserAuthentication:
    '''Тесты для аутентификации пользователей'''

    async def test_login_success(
        self,
        client: AsyncClient,
        test_user: User
    ):
        '''Тест успешного входа'''
        response = await client.post(
            '/auth/jwt/login',
            data={
                'username': test_user.email,
                'password': 'TestPass123!'
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        assert data['token_type'] == 'bearer'

    async def test_login_wrong_password(
        self,
        client: AsyncClient,
        test_user: User
    ):
        '''Тест входа с неверным паролем'''
        response = await client.post(
            '/auth/jwt/login',
            data={
                'username': test_user.email,
                'password': 'WrongPassword123!'
            }
        )

        assert response.status_code == 400

    async def test_login_nonexistent_user(self, client: AsyncClient):
        '''Тест входа несуществующего пользователя'''
        response = await client.post(
            '/auth/jwt/login',
            data={
                'username': 'nonexistent@example.com',
                'password': 'SomePassword123!'
            }
        )

        assert response.status_code == 400

    async def test_login_invalid_data(self, client: AsyncClient):
        '''Тест входа с невалидными данными'''
        response = await client.post(
            '/auth/jwt/login',
            data={
                'username': 'invalid-email',
                'password': 'SomePassword123!'
            }
        )

        assert response.status_code == 422
