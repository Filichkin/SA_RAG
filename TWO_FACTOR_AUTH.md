# Двухфакторная аутентификация (2FA)

## Обзор

В системе реализована двухфакторная аутентификация для повышения безопасности входа пользователей. Теперь процесс входа состоит из двух этапов:

1. **Первый этап**: Проверка email и пароля, отправка 6-значного кода на email
2. **Второй этап**: Проверка кода и выдача JWT токена

## API Эндпоинты

### 1. Первый этап входа - отправка кода

**POST** `/auth/2fa/login`

Отправляет 6-значный код на email пользователя после проверки пароля.

#### Запрос:
```json
{
    "email": "user@example.com",
    "password": "SecurePass123!"
}
```

#### Ответ (успех):
```json
{
    "message": "Код подтверждения отправлен на email",
    "temp_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Ответ (ошибка):
```json
{
    "detail": "Неверный email или пароль"
}
```

### 2. Второй этап входа - проверка кода

**POST** `/auth/2fa/verify-code`

Проверяет 6-значный код используя временный токен и выдает JWT токен.

#### Заголовки:
```
X-Temp-Token: <временный_токен_из_первого_этапа>
```

#### Запрос:
```json
{
    "code": "123456"
}
```

#### Ответ (успех):
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

#### Ответ (ошибка):
```json
{
    "detail": "Неверный код подтверждения"
}
```

### 3. Выход из системы

**POST** `/auth/logout`

Завершает сессию пользователя и инвалидирует токен.

#### Заголовки:
```
Authorization: Bearer <ваш_jwt_токен>
```

#### Ответ (успех):
```json
{
    "message": "Выход выполнен успешно"
}
```

#### Ответ (ошибка):
```json
{
    "detail": "Not authenticated"
}
```

## Особенности реализации

### Время действия кода
- Код действителен в течение **10 минут**
- После истечения времени код становится недействительным
- При истечении кода необходимо заново пройти первый этап входа

### Безопасность
- Код генерируется криптографически стойким способом
- Каждый код может быть использован только один раз
- При создании нового кода все предыдущие коды пользователя удаляются
- Код содержит только цифры (6 символов)

### Email уведомления
- Код отправляется на email, указанный при входе
- Email содержит инструкции по использованию кода
- В случае ошибки отправки email возвращается соответствующее сообщение

## Изменения в системе

### Отключенные эндпоинты
- Стандартный эндпоинт `/auth/jwt/login` отключен
- Теперь используется двухэтапная аутентификация

### Новые компоненты
- **Модель**: `TwoFactorAuthCode` - для хранения кодов
- **CRUD**: `TwoFactorAuthCRUD` - для работы с кодами
- **Схемы**: `TwoFactorAuthRequest`, `TwoFactorAuthVerifyCode`, `LogoutResponse`
- **Эндпоинты**: `/auth/2fa/login`, `/auth/2fa/verify-code`, `/auth/logout`

### База данных
- Добавлена таблица `two_factor_auth_codes`
- Создана миграция `f282f84f8ae7_add_two_factor_auth_codes_table.py`

## Пример использования

### cURL

#### Шаг 1 - Отправка кода:
```bash
curl -X POST "http://localhost:8000/auth/2fa/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "SecurePass123!"
     }'
```

#### Шаг 2 - Проверка кода:
```bash
curl -X POST "http://localhost:8000/auth/2fa/verify-code" \
     -H "Content-Type: application/json" \
     -H "X-Temp-Token: <временный_токен_из_первого_этапа>" \
     -d '{
       "code": "123456"
     }'
```

#### Шаг 3 - Выход из системы:
```bash
curl -X POST "http://localhost:8000/auth/logout" \
     -H "Authorization: Bearer <ваш_jwt_токен>"
```

### Python

```python
import httpx

async def login_with_2fa():
    async with httpx.AsyncClient() as client:
        # Шаг 1: Отправка кода
        response = await client.post(
            'http://localhost:8000/auth/2fa/login',
            json={
                'email': 'user@example.com',
                'password': 'SecurePass123!'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print('Код отправлен на email')
            temp_token = data['temp_token']
            
            # Шаг 2: Проверка кода
            code = input('Введите код из email: ')
            response = await client.post(
                'http://localhost:8000/auth/2fa/verify-code',
                headers={'X-Temp-Token': temp_token},
                json={'code': code}
            )
            
            if response.status_code == 200:
                token = response.json()['access_token']
                print(f'Успешный вход! Токен: {token}')
                
                # Шаг 3: Выход из системы
                logout_response = await client.post(
                    'http://localhost:8000/auth/logout',
                    headers={'Authorization': f'Bearer {token}'}
                )
                
                if logout_response.status_code == 200:
                    print('Успешный выход из системы!')
```

## Тестирование

Для тестирования системы используйте файл `test_2fa.py`:

```bash
python test_2fa.py
```

## Логирование

Все операции 2FA логируются в систему логирования приложения с использованием логгера `two_factor_auth`.

## Соответствие стандартам

- Код соответствует стандартам PEP 8
- Используются одинарные кавычки
- Избегается дублирование кода
- Применены принципы SOLID
