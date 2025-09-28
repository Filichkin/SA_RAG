# SA_RAG Agent

Система поддержки поиска компании с интеграцией RAG (Retrieval-Augmented Generation) и двухфакторной аутентификацией.

## 🚀 Возможности

- **Пользовательская система** с регистрацией, авторизацией и управлением профилями
- **Валидация паролей** с подтверждением при регистрации
- **Двухфакторная аутентификация** (2FA) с отправкой кодов по email
- **Сброс паролей** через email с временными токенами
- **AI агент** с интеграцией RAG для интеллектуального поиска и ответов
- **MCP RAG сервер** для работы с базой знаний через MCP протокол
- **RESTful API** с автоматической документацией (Swagger)
- **Логирование** с разделением по модулям
- **Тестирование** с покрытием всех компонентов

## 📁 Структура проекта

```
SA_RAG/
├── app/                          # Основное приложение
│   ├── api/                      # API эндпоинты
│   │   ├── endpoints/            # Конкретные эндпоинты
│   │   │   ├── user.py          # Пользовательские операции
│   │   │   ├── two_factor_auth.py # 2FA операции
│   │   │   └── ai_agent.py      # AI агент для работы с RAG
│   │   ├── routers.py            # Маршрутизация API
│   │   ├── utils.py              # Утилиты API
│   │   └── validators.py         # Валидаторы
│   ├── core/                     # Основная логика
│   │   ├── config.py             # Конфигурация
│   │   ├── db.py                 # База данных
│   │   ├── init_db.py            # Инициализация БД
│   │   └── user.py               # Пользовательская логика
│   ├── crud/                     # CRUD операции
│   ├── models/                   # SQLAlchemy модели
│   ├── schemas/                  # Pydantic схемы
│   ├── services/                 # Сервисы
│   │   ├── agent/               # AI агент
│   │   │   ├── ai_agent.py      # Основная логика агента
│   │   │   ├── mcp_client.py    # MCP клиент
│   │   │   └── system_prompt.txt # Системный промпт
│   │   └── mcp_rag/             # MCP RAG сервер
│   │       ├── server.py         # Основной сервер
│   │       └── quick_test.py     # Тестирование
│   ├── logging/                  # Система логирования
│   └── main.py                   # Точка входа
├── tests/                        # Тесты
├── alembic/                      # Миграции БД
├── requirements.txt              # Зависимости
└── README.md                     # Документация
```

## 🛠 Установка и настройка

### 1. Клонирование и установка зависимостей

```bash
git clone <repository-url>
cd SA_RAG
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# База данных
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=sa_rag_db

# Email настройки
YANDAX_EMAIL=your_email@yandex.ru
YANDEX_APP_PASS=your_app_password

# RAG API настройки
KEY_ID=your_key_id
KEY_SECRET=your_key_secret
AUTH_URL=https://your-auth-url
RETRIEVE_URL_TEMPLATE=https://your-retrieve-url
KNOWLEDGE_BASE_ID=your_kb_id
KNOWLEDGE_BASE_VERSION_ID=your_version_id
EVOLUTION_PROJECT_ID=your_project_id
RETRIEVE_LIMIT=6

# JWT настройки
SECRET=your_secret_key
JWT_TOKEN_LIFETIME=3600

# Первый суперпользователь
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin_password

# AI агент настройки
MCP_SERVER_URL=http://localhost:8003
MCP_TRANSPORT=sse
MCP_RAG_TOOL_NAME=request_to_rag
GIGACHAT_MODEL=GigaChat:latest
GIGACHAT_TEMPERATURE=0.1
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_CREDENTIALS=your_gigachat_credentials
GIGACHAT_VERIFY_SSL=true
```

### 3. Инициализация базы данных

```bash
# Создание миграций
alembic upgrade head

# Или через Makefile
make init-db
```

## 🚀 Запуск

### Основное приложение

```bash
# Запуск FastAPI сервера
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### MCP RAG сервер

```bash
# Запуск MCP RAG сервера
python -m app.services.mcp_rag.server
```

### AI агент

AI агент автоматически подключается к MCP RAG серверу через FastAPI endpoint `/ask_with_ai`. 
Убедитесь, что MCP RAG сервер запущен перед использованием AI агента.

## 🧪 Тестирование

### Запуск всех тестов

```bash
# Через pytest
pytest

# Через Makefile
make test

# Через скрипт
python run_tests.py
```

### Тестирование MCP RAG сервера

```bash
# Быстрый тест
python app/services/mcp_rag/quick_test.py "ваш запрос"

# Пример
python app/services/mcp_rag/quick_test.py "Какие условия гарантии Киа?"
```

### Доступные тесты

- `test_user_endpoints.py` - Тесты пользовательских эндпоинтов
- `test_two_factor_auth_temp_tokens.py` - Тесты 2FA
- `test_password_reset.py` - Тесты сброса паролей
- `test_user_integration.py` - Интеграционные тесты
- `test_user_validation.py` - Тесты валидации (включая валидацию паролей)
- `test_schemas_2fa.py` - Тесты схем двухфакторной аутентификации

## 📚 API Документация

После запуска приложения документация доступна по адресам:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Основные эндпоинты

#### Пользователи
- `POST /users/register` - Регистрация (требует подтверждение пароля)
- `POST /users/login` - Авторизация
- `GET /users/me` - Получение профиля
- `PUT /users/me` - Обновление профиля

#### Двухфакторная аутентификация
- `POST /2fa/send-code` - Отправка кода 2FA
- `POST /2fa/verify-code` - Проверка кода 2FA
- `POST /2fa/disable` - Отключение 2FA

#### Сброс паролей
- `POST /users/forgot-password` - Запрос сброса пароля
- `POST /users/reset-password` - Сброс пароля

#### AI агент
- `POST /ask_with_ai` - Задать вопрос AI ассистенту для поиска в базе знаний

## 🔐 Валидация паролей

### Регистрация с подтверждением пароля

При регистрации пользователя система требует подтверждения пароля для предотвращения ошибок ввода:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "Alex",
  "last_name": "Fill",
  "date_of_birth": "1992-05-20",
  "phone": "+79031234567"
}
```

### Правила валидации

- **Обязательные поля**: `password` и `password_confirm` должны совпадать
- **Минимальная длина**: 8 символов
- **Максимальная длина**: 128 символов
- **Требования безопасности**: минимум 1 буква, 1 цифра, 1 спецсимвол
- **Ошибка валидации**: При несовпадении паролей возвращается сообщение "Пароли не совпадают"

### Примеры ошибок

```json
// Несовпадающие пароли
{
  "password": "Password123!",
  "password_confirm": "DifferentPass123!"
}
// Ошибка: "Пароли не совпадают"

// Слабый пароль
{
  "password": "123",
  "password_confirm": "123"
}
// Ошибка: "Пароль не соответствует требованиям безопасности"
```

## 🔧 Разработка

### Структура кода

- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **Alembic** - миграции БД
- **Pydantic** - валидация данных
- **FastMCP** - MCP сервер для RAG
- **Pytest** - тестирование

### Логирование

Логи разделены по модулям:
- `app/logging/logs/user.log` - пользовательские операции
- `app/logging/logs/two_factor_auth.log` - 2FA операции

### Миграции

```bash
# Создание новой миграции
alembic revision --autogenerate -m "описание изменений"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

## 🐳 Docker (опционально)

```bash
# Сборка образа
docker build -t sa-rag-agent .

# Запуск контейнера
docker run -p 8000:8000 --env-file .env sa-rag-agent
```

## 📝 Переменные окружения

| Переменная | Описание | Обязательная |
|------------|----------|--------------|
| `POSTGRES_*` | Настройки БД | ✅ |
| `YANDAX_EMAIL` | Email для отправки | ✅ |
| `YANDEX_APP_PASS` | Пароль приложения | ✅ |
| `KEY_ID` | ID ключа RAG API | ✅ |
| `KEY_SECRET` | Секрет RAG API | ✅ |
| `AUTH_URL` | URL аутентификации RAG | ✅ |
| `RETRIEVE_URL_TEMPLATE` | URL для запросов RAG | ✅ |
| `KNOWLEDGE_BASE_ID` | ID базы знаний | ✅ |
| `EVOLUTION_PROJECT_ID` | ID проекта | ✅ |
| `MCP_SERVER_URL` | URL MCP сервера | ✅ |
| `MCP_TRANSPORT` | Транспорт MCP (sse) | ✅ |
| `GIGACHAT_CREDENTIALS` | Учетные данные GigaChat | ✅ |

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

Проект разработан для внутреннего использования компании.

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи в `app/logging/logs/`
2. Убедитесь, что все переменные окружения настроены
3. Проверьте подключение к базе данных
4. Запустите тесты для диагностики

---

**Версия**: 1.2.0  
**Последнее обновление**: Январь 2025

### История изменений

#### v1.2.0 (Январь 2025)
- ✅ Добавлена валидация паролей с подтверждением при регистрации
- ✅ Поле `password_confirm` в схеме `UserCreate`
- ✅ Валидация равенства паролей с понятными сообщениями об ошибках
- ✅ Обновлены все тесты для поддержки новой валидации
- ✅ Исправлена совместимость с базой данных (исключение `password_confirm` из сохранения)

#### v1.1.0 (Декабрь 2024)
- ✅ Базовая функциональность пользователей
- ✅ Двухфакторная аутентификация
- ✅ AI агент с RAG интеграцией
- ✅ MCP RAG сервер
