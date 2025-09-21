from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import generate_2fa_code, email_service
from app.core.constants import Constants, Messages, Descriptions
from app.core.db import get_async_session
from app.core.user import get_jwt_strategy
from app.crud.two_factor_auth import two_factor_auth_crud
from app.crud.user import user_crud
from app.logging import logging_config
from app.schemas.two_factor_auth import (
    TwoFactorAuthRequest,
    TwoFactorAuthVerify,
    TwoFactorAuthResponse,
    TwoFactorAuthTokenResponse
)

router = APIRouter()


@router.post(
    Constants.TWO_FA_LOGIN_PREFIX,
    response_model=TwoFactorAuthResponse,
    summary=Descriptions.TWO_FA_LOGIN_SUMMARY,
    description=Descriptions.TWO_FA_LOGIN_DESCRIPTION,
    tags=Constants.AUTH_TAGS
)
async def two_factor_auth_login(
    login_data: TwoFactorAuthRequest,
    session: AsyncSession = Depends(get_async_session)
):
    '''
    Первый этап входа с двухфакторной аутентификацией.
    Проверяет email и пароль, отправляет код на email.
    '''
    user_logger = logging_config.get_endpoint_logger('two_factor_auth')

    user_logger.info(
        f'Запрос на вход с 2FA для email: {login_data.email}'
    )

    try:
        # Ищем пользователя по email
        user = await user_crud.get_by_email(login_data.email, session)
        if not user:
            user_logger.warning(
                f'Попытка входа с несуществующим email: {login_data.email}'
            )
            raise HTTPException(
                status_code=Constants.HTTP_404_NOT_FOUND,
                detail=Messages.TWO_FA_INVALID_CREDENTIALS_MSG
            )

        # Проверяем пароль
        if not user_crud.verify_password(
            login_data.password, user.hashed_password
        ):
            user_logger.warning(
                f'Неверный пароль для пользователя {user.id} '
                f'(email: {user.email})'
            )
            raise HTTPException(
                status_code=Constants.HTTP_400_BAD_REQUEST,
                detail=Messages.TWO_FA_INVALID_CREDENTIALS_MSG
            )

        # Получаем данные пользователя для email и логирования
        user_id = user.id
        user_name = f'{user.first_name} {user.last_name}'
        user_email = user.email

        # Генерируем 6-значный код
        code = generate_2fa_code()

        # Сохраняем код в базе данных
        await two_factor_auth_crud.create_code(
            user_id=user_id,
            code=code,
            session=session
        )

        # Отправляем код на email
        email_sent = await email_service.send_2fa_code_email(
            to_email=user_email,
            code=code,
            user_name=user_name
        )

        if not email_sent:
            user_logger.error(
                f'Ошибка отправки 2FA кода для пользователя {user_id}'
            )
            raise HTTPException(
                status_code=Constants.HTTP_400_BAD_REQUEST,
                detail=Messages.EMAIL_SEND_ERROR_MSG
            )

        user_logger.info(
            f'2FA код отправлен пользователю {user_id} '
            f'(email: {user_email})'
        )

        return TwoFactorAuthResponse(
            message=Messages.TWO_FA_CODE_SENT_MSG
        )

    except HTTPException:
        # Перебрасываем HTTP исключения без дополнительного логирования
        raise
    except Exception as e:
        user_logger.error(
            f'Ошибка при входе с 2FA для email {login_data.email}: {str(e)}',
            exc_info=True
        )
        raise


@router.post(
    Constants.TWO_FA_VERIFY_PREFIX,
    response_model=TwoFactorAuthTokenResponse,
    summary=Descriptions.TWO_FA_VERIFY_SUMMARY,
    description=Descriptions.TWO_FA_VERIFY_DESCRIPTION,
    tags=Constants.AUTH_TAGS
)
async def two_factor_auth_verify(
    verify_data: TwoFactorAuthVerify,
    session: AsyncSession = Depends(get_async_session)
):
    '''
    Второй этап входа с двухфакторной аутентификацией.
    Проверяет 6-значный код и выдает токен доступа.
    '''
    user_logger = logging_config.get_endpoint_logger('two_factor_auth')

    user_logger.info(
        f'Запрос на проверку 2FA кода для email: {verify_data.email}'
    )

    try:
        # Ищем пользователя по email
        user = await user_crud.get_by_email(verify_data.email, session)
        if not user:
            user_logger.warning(
                f'Попытка проверки 2FA кода с несуществующим email: '
                f'{verify_data.email}'
            )
            raise HTTPException(
                status_code=Constants.HTTP_404_NOT_FOUND,
                detail=Messages.TWO_FA_INVALID_CREDENTIALS_MSG
            )

        # Получаем данные пользователя для логирования
        user_id = user.id
        user_email = user.email

        # Проверяем код
        two_fa_code = await two_factor_auth_crud.get_valid_code(
            user_id=user_id,
            code=verify_data.code,
            session=session
        )

        if not two_fa_code:
            user_logger.warning(
                f'Неверный или истекший 2FA код для пользователя {user_id}'
            )
            raise HTTPException(
                status_code=Constants.HTTP_400_BAD_REQUEST,
                detail=Messages.TWO_FA_CODE_INVALID_MSG
            )

        # Помечаем код как использованный
        await two_factor_auth_crud.mark_code_as_used(two_fa_code, session)

        # Генерируем JWT токен
        jwt_strategy = get_jwt_strategy()
        token = await jwt_strategy.write_token(user)

        user_logger.info(
            f'Успешный вход с 2FA для пользователя {user_id} '
            f'(email: {user_email})'
        )

        return TwoFactorAuthTokenResponse(
            access_token=token,
            token_type='bearer'
        )

    except HTTPException:
        # Перебрасываем HTTP исключения без дополнительного логирования
        raise
    except Exception as e:
        user_logger.error(
            f'Ошибка при проверке 2FA кода для email {verify_data.email}: '
            f'{str(e)}',
            exc_info=True
        )
        raise
