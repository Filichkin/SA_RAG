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
    TWO_FA_CODE_LEN = 6
    RAG_ENDPOINTS_PREFIX = '/api'
    RAG_ENDPOINTS_TAGS = ('RAG_Agent',)

    # HTTP Status Codes
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404

    # Pagination defaults
    DEFAULT_SKIP = 0
    DEFAULT_LIMIT = 10
    MAX_LIMIT = 100

    # User management endpoints
    GET_ALL_USERS_PREFIX = '/users'
    DELETE_USER_PREFIX = 'users/{user_id}'
    CHANGE_PASSWORD_PREFIX = '/users/change-password'
    RESET_PASSWORD_PREFIX = '/users/reset-password'

    # Two-factor authentication endpoints
    TWO_FA_LOGIN_PREFIX = '/auth/2fa/login'
    TWO_FA_VERIFY_CODE_PREFIX = '/auth/2fa/verify-code'
    LOGOUT_PREFIX = '/auth/logout'

    # AI Agent endpoints
    AI_ASK_PREFIX = '/ask_with_ai'
    AI_AGENT_TAGS = ('ai_agent',)
    AI_QUERY_MAX_LENGTH = 1000
    AI_QUERY_PREVIEW_LENGTH = 100


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
    INVALID_OLD_PASSWORD_MSG = 'Неверный текущий пароль'
    PASSWORD_CHANGED_SUCCESS_MSG = 'Пароль успешно изменен'
    RESET_PASSWORD_SUCCESS_MSG = 'Новый пароль отправлен на email'
    EMAIL_NOT_FOUND_MSG = 'Пользователь с указанным email не найден'
    EMAIL_SEND_ERROR_MSG = 'Ошибка отправки email'

    # Two-factor authentication messages
    TWO_FA_CODE_SENT_MSG = 'Код подтверждения отправлен на email'
    TWO_FA_CODE_INVALID_MSG = 'Неверный код подтверждения'
    TWO_FA_CODE_EXPIRED_MSG = 'Код подтверждения истек'
    TWO_FA_LOGIN_SUCCESS_MSG = 'Вход выполнен успешно'
    TWO_FA_INVALID_CREDENTIALS_MSG = 'Неверный email или пароль'
    LOGOUT_SUCCESS_MSG = 'Выход выполнен успешно'

    # AI Agent messages
    AI_EMPTY_QUERY_MSG = 'Запрос не может быть пустым'
    AI_QUERY_TOO_LONG_MSG = (
        'Запрос слишком длинный (максимум 1000 символов)'
    )
    AI_STREAM_ERROR_MSG = 'Ошибка при генерации ответа'
    AI_GENERAL_ERROR_MSG = (
        'К сожалению, произошла ошибка при обработке запроса'
    )


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
    CHANGE_PASSWORD_SUMMARY = 'Изменить пароль'
    CHANGE_PASSWORD_DESCRIPTION = (
        'Изменить пароль текущего пользователя. Требуется указать '
        'текущий пароль для подтверждения.'
    )
    RESET_PASSWORD_SUMMARY = 'Сбросить пароль'
    RESET_PASSWORD_DESCRIPTION = (
        'Сбросить пароль пользователя. Новый пароль будет отправлен на email. '
        'Все активные сессии будут завершены.'
    )

    # Two-factor authentication descriptions
    TWO_FA_LOGIN_SUMMARY = 'Вход с двухфакторной аутентификацией'
    TWO_FA_LOGIN_DESCRIPTION = (
        'Первый этап входа. Проверяет email и пароль, отправляет код на email.'
    )
    LOGOUT_SUMMARY = 'Выход из системы'
    LOGOUT_DESCRIPTION = (
        'Завершение сессии пользователя. Инвалидирует текущий токен.'
    )

    # AI Agent descriptions
    AI_ASK_SUMMARY = 'Задать вопрос AI ассистенту'
    AI_ASK_DESCRIPTION = (
        'Отправляет запрос к AI ассистенту для поиска информации в базе знаний'
    )
