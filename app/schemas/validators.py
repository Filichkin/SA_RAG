import re

from app.core.config import settings


def validate_password_strength(password: str) -> str:
    '''Общая функция валидации пароля для избежания дублирования кода'''
    if not password:
        raise ValueError('Пароль обязателен')

    password = password.strip()
    if len(password) < settings.user_password_min_len:
        raise ValueError(
            f'Пароль должен содержать минимум '
            f'{settings.user_password_min_len} символов'
        )
    if len(password) > settings.user_password_max_len:
        raise ValueError(
            f'Пароль должен содержать не более '
            f'{settings.user_password_max_len} символов'
        )

    if not re.fullmatch(settings.password_pattern, password):
        raise ValueError(
            'Пароль не соответствует требованиям безопасности: '
            'минимум 1 буква, 1 цифра и 1 спецсимвол'
        )
    return password


def validate_password_change(old_password: str, new_password: str) -> str:
    '''Валидация смены пароля с проверкой на совпадение со старым'''
    # Сначала проверяем силу нового пароля
    validated_new_password = validate_password_strength(new_password)

    # Проверяем, что новый пароль не совпадает со старым
    if old_password == validated_new_password:
        raise ValueError('Новый пароль не должен совпадать со старым')

    return validated_new_password
