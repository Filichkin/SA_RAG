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
)

app.include_router(main_router)
