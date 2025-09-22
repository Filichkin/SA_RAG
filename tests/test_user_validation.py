'''
Тесты для валидации данных пользователей
'''
import pytest
from datetime import date, timedelta

from app.schemas.user import UserCreate, UserUpdate, UserChangePassword
from app.schemas.validators import (
    validate_password_strength, validate_password_change
)


class TestPasswordValidation:
    '''Тесты валидации паролей'''

    def test_validate_password_strength_success(self):
        '''Тест успешной валидации пароля'''
        valid_passwords = [
            'StrongPass123!',
            'MySecure1@',
            'Test123$',
            'Password1&'
        ]

        for password in valid_passwords:
            result = validate_password_strength(password)
            assert result == password

    def test_validate_password_strength_empty(self):
        '''Тест валидации пустого пароля'''
        with pytest.raises(ValueError, match='Пароль обязателен'):
            validate_password_strength('')

    def test_validate_password_strength_whitespace_only(self):
        '''Тест валидации пароля из пробелов'''
        with pytest.raises(ValueError, match='Пароль обязателен'):
            validate_password_strength('   ')

    def test_validate_password_strength_too_short(self):
        '''Тест валидации слишком короткого пароля'''
        with pytest.raises(
            ValueError, match='Пароль должен содержать минимум'
        ):
            validate_password_strength('123')

    def test_validate_password_strength_no_letters(self):
        '''Тест валидации пароля без букв'''
        with pytest.raises(
            ValueError,
            match='Пароль не соответствует требованиям безопасности'
        ):
            validate_password_strength('123456789!')

    def test_validate_password_strength_no_digits(self):
        '''Тест валидации пароля без цифр'''
        with pytest.raises(
            ValueError,
            match='Пароль не соответствует требованиям безопасности'
        ):
            validate_password_strength('Password!')

    def test_validate_password_strength_no_special_chars(self):
        '''Тест валидации пароля без спецсимволов'''
        with pytest.raises(
            ValueError,
            match='Пароль не соответствует требованиям безопасности'
        ):
            validate_password_strength('Password123')

    def test_validate_password_change_success(self):
        '''Тест успешной валидации смены пароля'''
        old_password = 'OldPass123!'
        new_password = 'NewPass456!'

        result = validate_password_change(old_password, new_password)
        assert result == new_password

    def test_validate_password_change_same_password(self):
        '''Тест валидации смены пароля на тот же'''
        password = 'SamePass123!'

        with pytest.raises(
            ValueError,
            match='Новый пароль не должен совпадать со старым'
        ):
            validate_password_change(password, password)


class TestUserSchemaValidation:
    '''Тесты валидации схем пользователей'''

    def test_user_create_valid(self):
        '''Тест валидной схемы создания пользователя'''
        user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': '1990-01-01',
            'phone': '+79031234567'
        }

        user = UserCreate(**user_data)
        assert user.email == user_data['email']
        assert user.first_name == user_data['first_name']
        assert user.last_name == user_data['last_name']
        assert user.phone == user_data['phone']

    def test_user_create_invalid_email(self):
        '''Тест невалидного email'''
        user_data = {
            'email': 'invalid-email',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

        with pytest.raises(ValueError):
            UserCreate(**user_data)

    def test_user_create_weak_password(self):
        '''Тест слабого пароля'''
        user_data = {
            'email': 'test@example.com',
            'password': '123',
            'first_name': 'Test',
            'last_name': 'User'
        }

        with pytest.raises(ValueError):
            UserCreate(**user_data)

    def test_user_create_invalid_phone(self):
        '''Тест невалидного телефона'''
        user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '123'  # Невалидный формат
        }

        with pytest.raises(ValueError, match='Телефон должен быть в формате'):
            UserCreate(**user_data)

    def test_user_create_future_birth_date(self):
        '''Тест даты рождения в будущем'''
        future_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': future_date
        }

        with pytest.raises(
            ValueError,
            match='Дата рождения не может быть в будущем'
        ):
            UserCreate(**user_data)

    def test_user_create_empty_name(self):
        '''Тест пустого имени'''
        user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': '',
            'last_name': 'User'
        }

        with pytest.raises(ValueError):
            UserCreate(**user_data)

    def test_user_create_long_name(self):
        '''Тест слишком длинного имени'''
        long_name = 'A' * 51  # Превышает максимальную длину
        user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': long_name,
            'last_name': 'User'
        }

        with pytest.raises(ValueError):
            UserCreate(**user_data)

    def test_user_update_valid(self):
        '''Тест валидной схемы обновления пользователя'''
        user_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '+79031234568'
        }

        user = UserUpdate(**user_data)
        assert user.first_name == user_data['first_name']
        assert user.last_name == user_data['last_name']
        assert user.phone == user_data['phone']

    def test_user_update_partial(self):
        '''Тест частичного обновления пользователя'''
        user_data = {
            'first_name': 'Updated'
        }

        user = UserUpdate(**user_data)
        assert user.first_name == user_data['first_name']
        assert user.last_name is None

    def test_user_change_password_valid(self):
        '''Тест валидной схемы смены пароля'''
        password_data = {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass456!'
        }

        password_change = UserChangePassword(**password_data)
        assert password_change.old_password == password_data['old_password']
        assert password_change.new_password == password_data['new_password']

    def test_user_change_password_same_passwords(self):
        '''Тест смены пароля на тот же'''
        password_data = {
            'old_password': 'SamePass123!',
            'new_password': 'SamePass123!'
        }

        with pytest.raises(
            ValueError,
            match='Новый пароль не должен совпадать со старым'
        ):
            UserChangePassword(**password_data)


class TestPhoneValidation:
    '''Тесты валидации телефонов'''

    def test_valid_phone_formats(self):
        '''Тест валидных форматов телефонов'''
        valid_phones = [
            '+79031234567',
            '+79999999999',
            '+79000000000'
        ]

        for phone in valid_phones:
            user_data = {
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'first_name': 'Test',
                'last_name': 'User',
                'phone': phone
            }
            user = UserCreate(**user_data)
            assert user.phone == phone

    def test_invalid_phone_formats(self):
        '''Тест невалидных форматов телефонов'''
        invalid_phones = [
            '123',
            '+7903123456',  # Недостаточно цифр
            '+790312345678',  # Слишком много цифр
            '89031234567',  # Без +
            '+89031234567',  # Неправильный код страны
            '+7 903 123 45 67',  # С пробелами
            '+7-903-123-45-67'  # С дефисами
        ]

        for phone in invalid_phones:
            user_data = {
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'first_name': 'Test',
                'last_name': 'User',
                'phone': phone
            }
            with pytest.raises(
                ValueError, match='Телефон должен быть в формате'
            ):
                UserCreate(**user_data)

    def test_empty_phone(self):
        '''Тест пустого телефона'''
        user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': ''
        }

        user = UserCreate(**user_data)
        assert user.phone is None

    def test_none_phone(self):
        '''Тест None телефона'''
        user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': None
        }

        user = UserCreate(**user_data)
        assert user.phone is None


class TestDateValidation:
    '''Тесты валидации дат'''

    def test_valid_birth_dates(self):
        '''Тест валидных дат рождения'''
        valid_dates = [
            '1990-01-01',
            '2000-12-31',
            '1985-06-15'
        ]

        for birth_date in valid_dates:
            user_data = {
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'first_name': 'Test',
                'last_name': 'User',
                'date_of_birth': birth_date
            }
            user = UserCreate(**user_data)
            assert str(user.date_of_birth) == birth_date

    def test_future_birth_date(self):
        '''Тест даты рождения в будущем'''
        future_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': future_date
        }

        with pytest.raises(
            ValueError,
            match='Дата рождения не может быть в будущем'
        ):
            UserCreate(**user_data)

    def test_today_birth_date(self):
        '''Тест даты рождения сегодня'''
        today = date.today().strftime('%Y-%m-%d')
        user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': today
        }

        user = UserCreate(**user_data)
        assert str(user.date_of_birth) == today

    def test_none_birth_date(self):
        '''Тест None даты рождения'''
        user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': None
        }

        user = UserCreate(**user_data)
        assert user.date_of_birth is None
