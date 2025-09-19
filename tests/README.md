# Тесты для User Endpoints

Этот каталог содержит автотесты для endpoints пользователей в приложении SA_RAG.

## Структура тестов

### Основные файлы

- `conftest.py` - Конфигурация pytest, фикстуры и настройки
- `test_user_endpoints.py` - Основные тесты для всех endpoints пользователей
- `test_user_validation.py` - Тесты валидации данных пользователей
- `test_user_integration.py` - Интеграционные тесты и тесты безопасности
- `test_utils.py` - Утилиты для создания тестовых данных

### Типы тестов

#### 1. Unit тесты (`test_user_validation.py`)
- Валидация паролей
- Валидация схем пользователей
- Валидация телефонов
- Валидация дат

#### 2. API тесты (`test_user_endpoints.py`)
- Тесты для всех endpoints:
  - `GET /users` - получение всех пользователей
  - `DELETE /users/{user_id}` - удаление пользователя
  - `POST /users/change-password` - смена пароля
  - `POST /auth/register` - регистрация
  - `POST /auth/jwt/login` - аутентификация
- Тесты авторизации и прав доступа
- Тесты пагинации
- Тесты обработки ошибок

#### 3. Интеграционные тесты (`test_user_integration.py`)
- Полный workflow пользователя
- Конкурентные операции
- Тесты безопасности (SQL injection, XSS)
- Тесты производительности

## Запуск тестов

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск всех тестов

```bash
pytest
```

### Запуск конкретных тестов

```bash
# Только unit тесты
pytest tests/test_user_validation.py

# Только API тесты
pytest tests/test_user_endpoints.py

# Только интеграционные тесты
pytest tests/test_user_integration.py

# Тесты с маркерами
pytest -m "not slow"
pytest -m "integration"
```

### Запуск с подробным выводом

```bash
pytest -v
```

### Запуск с покрытием кода (если установлен pytest-cov)

```bash
pytest --cov=app --cov-report=html
```

## Фикстуры

### Основные фикстуры

- `client` - HTTP клиент для тестов
- `db_session` - Сессия базы данных для тестов
- `test_user` - Обычный тестовый пользователь
- `test_admin_user` - Тестовый администратор
- `test_superuser` - Тестовый суперпользователь

### Фикстуры авторизации

- `auth_headers` - Заголовки авторизации для обычного пользователя
- `admin_auth_headers` - Заголовки авторизации для администратора
- `superuser_auth_headers` - Заголовки авторизации для суперпользователя

## Тестовые данные

### Создание тестовых данных

Используйте утилиты из `test_utils.py`:

```python
from tests.test_utils import TestDataFactory

# Создание данных пользователя
user_data = TestDataFactory.create_user_data()

# Создание данных администратора
admin_data = TestDataFactory.create_admin_user_data()

# Создание невалидных данных
invalid_data = TestDataFactory.create_invalid_user_data()
```

### Константы

Используйте константы из `TestConstants`:

```python
from tests.test_utils import TestConstants

# Валидные данные
email = TestConstants.VALID_EMAIL
password = TestConstants.VALID_PASSWORD

# HTTP статус коды
assert response.status_code == TestConstants.OK
```

## Маркеры тестов

- `@pytest.mark.slow` - Медленные тесты
- `@pytest.mark.integration` - Интеграционные тесты
- `@pytest.mark.unit` - Unit тесты
- `@pytest.mark.auth` - Тесты требующие аутентификации
- `@pytest.mark.admin` - Тесты требующие права администратора
- `@pytest.mark.superuser` - Тесты требующие права суперпользователя

## Примеры тестов

### Простой тест endpoint

```python
async def test_get_user_success(client: AsyncClient, auth_headers: dict):
    response = await client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert "email" in response.json()
```

### Тест с созданием данных

```python
async def test_create_user(client: AsyncClient):
    user_data = TestDataFactory.create_user_data()
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 201
```

### Тест с мокированием

```python
async def test_with_mock(client: AsyncClient, mocker):
    mocker.patch('app.crud.user_crud.get_user', return_value=None)
    response = await client.get("/users/999")
    assert response.status_code == 404
```

## Отладка тестов

### Запуск одного теста

```bash
pytest tests/test_user_endpoints.py::TestGetAllUsers::test_get_all_users_success_admin -v
```

### Запуск с отладочным выводом

```bash
pytest -s -v
```

### Запуск с остановкой на первой ошибке

```bash
pytest -x
```

## Лучшие практики

1. **Именование тестов** - используйте описательные имена
2. **Изоляция тестов** - каждый тест должен быть независимым
3. **Очистка данных** - используйте фикстуры для создания/удаления тестовых данных
4. **Асинхронность** - используйте `pytest-asyncio` для асинхронных тестов
5. **Мокирование** - мокайте внешние зависимости
6. **Покрытие кода** - стремитесь к высокому покрытию кода тестами

## Troubleshooting

### Проблемы с базой данных

Убедитесь что тестовая база данных создается и очищается правильно:

```python
# В conftest.py настроена автоматическая очистка
@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # Создание и очистка БД для каждого теста
```

### Проблемы с аутентификацией

Проверьте что токены генерируются правильно:

```python
# Убедитесь что пользователь создан и токен валиден
response = await client.post("/auth/jwt/login", data={"username": email, "password": password})
assert response.status_code == 200
```

### Проблемы с зависимостями

Убедитесь что все зависимости установлены:

```bash
pip install pytest pytest-asyncio httpx pytest-mock
```
