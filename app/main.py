from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings
from app.core.init_db import create_first_superuser


logging.basicConfig(
    level=logging.INFO,
    format=settings.logging_format,
    datefmt=settings.logging_dt_format
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_first_superuser()
    yield

app = FastAPI(
    title=settings.app_title,
    description="""
    ## Двухфакторная аутентификация (2FA)

    Система использует двухфакторную аутентификацию для повышения безопасности.

    ### Процесс входа:

    1. **Первый этап** - Отправка кода:
       - POST `/auth/2fa/login` с email и паролем
       - Получите 6-значный код на email (действителен 10 минут)

    2. **Второй этап** - Проверка кода:
       - POST `/auth/2fa/verify` с email и кодом
       - Получите JWT токен для авторизации

    ### Использование токена:
    После получения токена используйте его в заголовке:
    ```
    Authorization: Bearer <ваш_токен>
    ```
    """,
    lifespan=lifespan,
    # Добавляем схему безопасности для Swagger
    openapi_tags=[
        {
            "name": "auth",
            "description": "Двухфакторная аутентификация",
        },
        {
            "name": "users",
            "description": "Управление пользователями",
        },
    ]
)


# Добавляем кастомную схему безопасности для Swagger
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )

    # Добавляем схему безопасности Bearer
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Введите JWT токен, полученный через 2FA"
        }
    }

    # Применяем схему безопасности ко всем эндпоинтам кроме 2FA
    for path in openapi_schema['paths']:
        for method in openapi_schema['paths'][path]:
            if path not in [
                '/auth/2fa/login',
                '/auth/2fa/verify',
                '/auth/2fa/verify-code'
            ]:
                # Переопределяем схему безопасности на нашу BearerAuth
                openapi_schema['paths'][path][method]['security'] = [
                    {'BearerAuth': []}
                ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


app.include_router(main_router)
