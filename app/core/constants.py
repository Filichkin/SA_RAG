from app.core.config import settings


class Constants:
    AUTH_PREFIX = '/auth/jwt'
    AUTH_TAGS = ('auth',)
    REGISTER_PREFIX = '/auth'
    USERS_PREFIX = '/users'
    USERS_TAGS = ('users',)
    JWT_TOKEN_URL = 'auth/jwt/login'
    JWT_AUTH_BACKEND_NAME = 'jwt'
    NAME_MIN_LEN = 1
    NAME_MAX_LEN = 50
    STRING_LEN = 120
    RAG_ENDPOINTS_PREFIX = '/api'
    RAG_ENDPOINTS_TAGS = ('RAG_Agent',)

    # HTTP Status Codes
    HTTP_400_BAD_REQUEST = 400
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404

    # Pagination defaults
    DEFAULT_SKIP = 0
    DEFAULT_LIMIT = 10
    MAX_LIMIT = 100

    # User management endpoints
    GET_ALL_USERS_PREFIX = '/users'
    DELETE_USER_PREFIX = 'users/{user_id}'


class Messages:
    PASSWORD_TOO_SHORT = (
        f'Password must be not less {settings.user_password_min_len}'
    )
    EMAIL_IN_PASSWORD = 'Password should`t contain email'
    USER_REGISTERED = 'User registered: '

    # Error messages
    INSUFFICIENT_PERMISSIONS_MSG = (
        'Недостаточно прав. Требуется роль администратора или '
        'суперпользователя.'
    )
    CANNOT_DELETE_SELF_MSG = 'Нельзя удалить самого себя'
    USER_NOT_FOUND_MSG = 'Пользователь не найден'


class Descriptions:
    # Query descriptions
    SKIP_DESCRIPTION = 'Количество записей для пропуска'
    LIMIT_DESCRIPTION = 'Максимальное количество записей'

    # Endpoint summaries and descriptions
    GET_ALL_USERS_SUMMARY = 'Получить всех пользователей'
    GET_ALL_USERS_DESCRIPTION = (
        'Получить список всех пользователей. Доступно только '
        'администраторам и суперпользователям.'
    )
    DELETE_USER_SUMMARY = 'Удалить пользователя'
    DELETE_USER_DESCRIPTION = (
        'Удалить пользователя по ID. Доступно только суперпользователям.'
    )
