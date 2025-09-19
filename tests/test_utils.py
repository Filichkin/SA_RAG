'''
Утилиты для тестов
'''
import random
import string
from datetime import date, timedelta
from typing import Dict, Any


def generate_random_email() -> str:
    '''Генерирует случайный email для тестов'''
    username = ''.join(random.choices(string.ascii_lowercase, k=8))
    domain = random.choice(['example.com', 'test.com', 'demo.org'])
    return f'{username}@{domain}'


def generate_random_phone() -> str:
    '''Генерирует случайный российский номер телефона'''
    number = ''.join(random.choices(string.digits, k=10))
    return f'+7{number}'


def generate_random_password() -> str:
    '''Генерирует случайный валидный пароль'''
    # Генерируем пароль с минимум 1 буквой, 1 цифрой и 1 спецсимволом
    letters = ''.join(random.choices(string.ascii_letters, k=6))
    digits = ''.join(random.choices(string.digits, k=2))
    special = random.choice('!@#$%^&*')
    password = letters + digits + special
    return ''.join(random.sample(password, len(password)))


def generate_random_name(length: int = 8) -> str:
    '''Генерирует случайное имя заданной длины'''
    return ''.join(random.choices(string.ascii_letters, k=length)).capitalize()


def generate_random_birth_date() -> str:
    '''Генерирует случайную дату рождения в прошлом'''
    start_date = date(1950, 1, 1)
    end_date = date(2000, 12, 31)

    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randint(0, days_between)

    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime('%Y-%m-%d')


def create_test_user_data(**overrides) -> Dict[str, Any]:
    '''Создает данные тестового пользователя с возможностью переопределения'''
    default_data = {
        'email': generate_random_email(),
        'password': generate_random_password(),
        'first_name': generate_random_name(),
        'last_name': generate_random_name(),
        'date_of_birth': generate_random_birth_date(),
        'phone': generate_random_phone()
    }

    default_data.update(overrides)
    return default_data


def create_test_user_update_data(**overrides) -> Dict[str, Any]:
    '''Создает данные для обновления пользователя'''
    default_data = {
        'first_name': generate_random_name(),
        'last_name': generate_random_name(),
        'phone': generate_random_phone()
    }

    default_data.update(overrides)
    return default_data


def create_test_password_change_data(**overrides) -> Dict[str, Any]:
    '''Создает данные для смены пароля'''
    default_data = {
        'old_password': 'OldTestPass123!',
        'new_password': generate_random_password()
    }

    default_data.update(overrides)
    return default_data


class TestDataFactory:
    '''Фабрика для создания тестовых данных'''

    @staticmethod
    def create_user_data(email: str = None, **kwargs) -> Dict[str, Any]:
        '''Создает данные пользователя'''
        return create_test_user_data(email=email, **kwargs)

    @staticmethod
    def create_admin_user_data(**kwargs) -> Dict[str, Any]:
        '''Создает данные администратора'''
        return create_test_user_data(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            **kwargs
        )

    @staticmethod
    def create_superuser_data(**kwargs) -> Dict[str, Any]:
        '''Создает данные суперпользователя'''
        return create_test_user_data(
            email='superuser@example.com',
            first_name='Super',
            last_name='User',
            **kwargs
        )

    @staticmethod
    def create_invalid_user_data(**kwargs) -> Dict[str, Any]:
        '''Создает невалидные данные пользователя'''
        return {
            'email': 'invalid-email',
            'password': '123',
            'first_name': '',
            'last_name': 'A' * 100,
            'phone': 'invalid-phone',
            'date_of_birth': '2030-01-01',
            **kwargs
        }


# Константы для тестов
class TestConstants:
    '''Константы для тестов'''

    # Валидные тестовые данные
    VALID_EMAIL = 'test@example.com'
    VALID_PASSWORD = 'TestPass123!'
    VALID_PHONE = '+79031234567'
    VALID_FIRST_NAME = 'Test'
    VALID_LAST_NAME = 'User'
    VALID_BIRTH_DATE = '1990-01-01'

    # Невалидные тестовые данные
    INVALID_EMAIL = 'invalid-email'
    INVALID_PASSWORD = '123'
    INVALID_PHONE = '123'
    INVALID_FIRST_NAME = ''
    INVALID_LAST_NAME = 'A' * 100
    INVALID_BIRTH_DATE = '2030-01-01'

    # Тестовые роли
    REGULAR_USER_ROLE = 'user'
    ADMIN_ROLE = 'admin'
    SUPERUSER_ROLE = 'superuser'

    # HTTP статус коды
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500


# Декораторы для тестов
def skip_if_no_database(func):
    '''Пропускает тест если база данных недоступна'''
    import pytest
    return pytest.mark.skipif(
        not hasattr(func, '_database_available'),
        reason='Database not available'
    )(func)


def requires_auth(func):
    '''Помечает тест как требующий аутентификации'''
    func._requires_auth = True
    return func


def requires_admin(func):
    '''Помечает тест как требующий права администратора'''
    func._requires_admin = True
    return func


def requires_superuser(func):
    '''Помечает тест как требующий права суперпользователя'''
    func._requires_superuser = True
    return func
