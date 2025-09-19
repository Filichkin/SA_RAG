# Руководство по тестированию SA_RAG

Этот документ описывает систему тестирования для проекта SA_RAG, включая автотесты для endpoints пользователей.

## Обзор

Проект включает комплексную систему тестирования, покрывающую:

- **Unit тесты** - тестирование отдельных компонентов и валидации
- **API тесты** - тестирование HTTP endpoints
- **Интеграционные тесты** - тестирование взаимодействия компонентов
- **Тесты безопасности** - проверка защиты от атак
- **Тесты производительности** - проверка времени ответа

## Структура тестов

```
tests/
├── __init__.py                 # Пакет тестов
├── conftest.py                 # Конфигурация pytest и фикстуры
├── test_user_endpoints.py      # Тесты API endpoints
├── test_user_validation.py     # Тесты валидации данных
├── test_user_integration.py    # Интеграционные тесты
├── test_utils.py              # Утилиты для тестов
├── examples.py                # Примеры использования
└── README.md                  # Документация тестов
```

## Установка и настройка

### 1. Установка зависимостей

```bash
# Установка основных зависимостей
pip install -r requirements.txt

# Или установка зависимостей для разработки
make dev-install
```

### 2. Настройка окружения

Создайте файл `.env.test` для тестового окружения:

```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=test-secret-key
TESTING=true
```

## Запуск тестов

### Основные команды

```bash
# Запуск всех тестов
make test
# или
pytest tests/ -v

# Запуск конкретных типов тестов
make test-unit      # Unit тесты
make test-api       # API тесты  
make test-integration  # Интеграционные тесты

# Запуск с покрытием кода
make test-coverage

# Запуск быстрых тестов (исключить медленные)
make test-fast
```

### Запуск через Makefile

```bash
# Показать все доступные команды
make help

# Установить зависимости
make install

# Запустить все тесты
make test

# Очистить временные файлы
make clean
```

### Запуск через скрипт

```bash
python run_tests.py
```

## Типы тестов

### 1. Unit тесты (`test_user_validation.py`)

Тестируют отдельные функции и валидацию:

```python
def test_validate_password_strength_success():
    """Тест успешной валидации пароля"""
    result = validate_password_strength("StrongPass123!")
    assert result == "StrongPass123!"

def test_validate_password_strength_weak():
    """Тест валидации слабого пароля"""
    with pytest.raises(ValueError):
        validate_password_strength("123")
```

### 2. API тесты (`test_user_endpoints.py`)

Тестируют HTTP endpoints:

```python
async def test_get_all_users_success_admin(
    client: AsyncClient, 
    admin_auth_headers: dict
):
    """Тест получения всех пользователей администратором"""
    response = await client.get("/users", headers=admin_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### 3. Интеграционные тесты (`test_user_integration.py`)

Тестируют полные сценарии использования:

```python
async def test_complete_user_workflow(client: AsyncClient):
    """Тест полного жизненного цикла пользователя"""
    # 1. Регистрация
    user_data = TestDataFactory.create_user_data()
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    
    # 2. Вход
    login_response = await client.post("/auth/jwt/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })
    assert login_response.status_code == 200
    
    # 3. Получение информации о себе
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_response = await client.get("/users/me", headers=headers)
    assert me_response.status_code == 200
```

## Фикстуры

### Основные фикстуры

- `client` - HTTP клиент для тестов
- `db_session` - Сессия базы данных
- `test_user` - Обычный пользователь
- `test_admin_user` - Администратор
- `test_superuser` - Суперпользователь

### Фикстуры авторизации

- `auth_headers` - Заголовки для обычного пользователя
- `admin_auth_headers` - Заголовки для администратора
- `superuser_auth_headers` - Заголовки для суперпользователя

### Использование фикстур

```python
async def test_with_fixtures(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Пример использования фикстур"""
    # test_user уже создан
    assert test_user.email is not None
    
    # auth_headers настроены для test_user
    response = await client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
```

## Утилиты для тестов

### TestDataFactory

Создание тестовых данных:

```python
from tests.test_utils import TestDataFactory

# Создание данных пользователя
user_data = TestDataFactory.create_user_data()

# Создание данных администратора
admin_data = TestDataFactory.create_admin_user_data()

# Создание невалидных данных
invalid_data = TestDataFactory.create_invalid_user_data()
```

### TestConstants

Использование констант:

```python
from tests.test_utils import TestConstants

# HTTP статус коды
assert response.status_code == TestConstants.OK
assert response.status_code == TestConstants.CREATED

# Валидные данные
email = TestConstants.VALID_EMAIL
password = TestConstants.VALID_PASSWORD
```

## Маркеры тестов

Используйте маркеры для категоризации тестов:

```python
@pytest.mark.slow
async def test_slow_operation():
    """Медленный тест"""
    pass

@pytest.mark.integration
async def test_integration():
    """Интеграционный тест"""
    pass

@pytest.mark.auth
async def test_requires_auth():
    """Тест требующий аутентификации"""
    pass
```

Запуск тестов по маркерам:

```bash
# Только быстрые тесты
pytest -m "not slow"

# Только интеграционные тесты
pytest -m "integration"

# Только тесты аутентификации
pytest -m "auth"
```

## Параметризованные тесты

```python
@pytest.mark.parametrize("email,expected_status", [
    ("valid@example.com", 201),
    ("invalid-email", 422),
    ("", 422),
])
async def test_email_validation(email, expected_status):
    """Тест валидации email"""
    user_data = TestDataFactory.create_user_data(email=email)
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == expected_status
```

## Мокирование

```python
async def test_with_mock(client: AsyncClient, mocker):
    """Пример использования моков"""
    # Мокаем метод для имитации ошибки
    from app.crud import user_crud
    mocker.patch.object(
        user_crud,
        'get_user_by_id',
        side_effect=Exception("Database error")
    )
    
    response = await client.get("/users/1")
    assert response.status_code in [500, 422]
```

## Тесты безопасности

```python
async def test_sql_injection_protection(client: AsyncClient):
    """Тест защиты от SQL инъекций"""
    malicious_input = "'; DROP TABLE users; --"
    
    response = await client.post("/auth/jwt/login", data={
        "username": malicious_input,
        "password": "password"
    })
    
    # Должен возвращать ошибку валидации
    assert response.status_code in [400, 422]

async def test_xss_protection(client: AsyncClient):
    """Тест защиты от XSS"""
    xss_payload = "<script>alert('xss')</script>"
    
    user_data = TestDataFactory.create_user_data(
        first_name=xss_payload
    )
    
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 422
```

## Покрытие кода

```bash
# Запуск с покрытием
make test-coverage

# Или напрямую
pytest --cov=app --cov-report=html --cov-report=term-missing
```

Отчет о покрытии будет создан в папке `htmlcov/`.

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

### Запуск с подробным выводом ошибок

```bash
pytest --tb=long
```

## Лучшие практики

### 1. Именование тестов

```python
# Хорошо
async def test_get_user_success_with_valid_id():
    """Тест успешного получения пользователя с валидным ID"""
    pass

# Плохо
async def test_user():
    """Тест пользователя"""
    pass
```

### 2. Структура тестов

```python
class TestGetUser:
    """Группировка связанных тестов"""
    
    async def test_success(self):
        """Тест успешного сценария"""
        pass
    
    async def test_not_found(self):
        """Тест ошибки 404"""
        pass
    
    async def test_unauthorized(self):
        """Тест ошибки 401"""
        pass
```

### 3. Изоляция тестов

```python
# Каждый тест должен быть независимым
async def test_create_user(client: AsyncClient):
    """Тест создания пользователя"""
    user_data = TestDataFactory.create_user_data()
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 201

async def test_get_user(client: AsyncClient, test_user: User):
    """Тест получения пользователя"""
    # test_user создается автоматически
    response = await client.get(f"/users/{test_user.id}")
    assert response.status_code == 200
```

### 4. Очистка данных

```python
# Фикстуры автоматически очищают данные между тестами
@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Создание и очистка БД для каждого теста"""
    # Создание БД
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            yield session
    # Очистка БД
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
```

## Troubleshooting

### Проблемы с базой данных

```bash
# Очистка тестовой БД
rm test.db

# Перезапуск тестов
make clean && make test
```

### Проблемы с зависимостями

```bash
# Переустановка зависимостей
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Проблемы с аутентификацией

Проверьте что токены генерируются правильно:

```python
# В conftest.py
@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    response = await client.post("/auth/jwt/login", data={
        "username": test_user.email,
        "password": "TestPass123!"
    })
    assert response.status_code == 200  # Проверка успешного входа
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

## CI/CD интеграция

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.12
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest tests/ --cov=app --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Заключение

Эта система тестирования обеспечивает:

- **Полное покрытие** всех endpoints пользователей
- **Автоматическую проверку** валидации данных
- **Тестирование безопасности** и производительности
- **Простое добавление** новых тестов
- **Интеграцию с CI/CD** системами

Для получения дополнительной информации см. `tests/README.md` и примеры в `tests/examples.py`.
