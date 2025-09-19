from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import current_admin_or_superuser
from app.core.constants import Constants, Messages, Descriptions
from app.core.db import get_async_session
from app.core.user import (
    auth_backend, fastapi_users, current_superuser, current_user
)
from app.crud.user import user_crud
from app.logging import logging_config
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserRead, UserUpdate, UserChangePassword
)


router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=Constants.AUTH_PREFIX,
    tags=Constants.AUTH_TAGS,
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=Constants.REGISTER_PREFIX,
    tags=Constants.AUTH_TAGS,
)
users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    route for route in users_router.routes if route.name != 'users:delete_user'
]
router.include_router(
    users_router,
    prefix=Constants.USERS_PREFIX,
    tags=Constants.USERS_TAGS,
)


@router.get(
    Constants.GET_ALL_USERS_PREFIX,
    response_model=List[UserRead],
    summary=Descriptions.GET_ALL_USERS_SUMMARY,
    description=Descriptions.GET_ALL_USERS_DESCRIPTION,
    tags=Constants.USERS_TAGS
)
async def get_all_users(
    skip: int = Query(
        Constants.DEFAULT_SKIP,
        ge=0,
        description=Descriptions.SKIP_DESCRIPTION
    ),
    limit: int = Query(
        Constants.DEFAULT_LIMIT,
        ge=1,
        le=Constants.MAX_LIMIT,
        description=Descriptions.LIMIT_DESCRIPTION
    ),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_admin_or_superuser)
):
    '''
    Получить всех пользователей с пагинацией.
    Доступно только пользователям с ролью администратора или суперпользователя.
    '''
    user_logger = logging_config.get_endpoint_logger('user')

    user_logger.info(
        f'Запрос на получение всех пользователей от пользователя '
        f'{current_user.id} (email: {current_user.email}, роль: '
        f'{"admin" if current_user.is_administrator else "superuser"})'
    )

    try:
        users = await user_crud.get_all_users(session, skip=skip, limit=limit)
        user_logger.info(
            f'Успешно получено {len(users)} пользователей '
            f'(skip={skip}, limit={limit})'
        )
        return users
    except Exception as e:
        user_logger.error(
            f'Ошибка при получении пользователей: {str(e)}',
            exc_info=True
        )
        raise


@router.delete(
    Constants.DELETE_USER_PREFIX,
    response_model=UserRead,
    summary=Descriptions.DELETE_USER_SUMMARY,
    description=Descriptions.DELETE_USER_DESCRIPTION,
    tags=Constants.USERS_TAGS
)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_superuser)
):
    '''
    Удалить пользователя по ID.
    Доступно только суперпользователям.
    '''
    user_logger = logging_config.get_endpoint_logger('user')

    user_logger.info(
        f'Запрос на удаление пользователя {user_id} от суперпользователя '
        f'{current_user.id} (email: {current_user.email})'
    )

    # Проверяем, что пользователь не пытается удалить самого себя
    if user_id == current_user.id:
        user_logger.warning(
            f'Попытка удаления самого себя: пользователь {current_user.id} '
            f'пытается удалить себя'
        )
        raise HTTPException(
            status_code=Constants.HTTP_400_BAD_REQUEST,
            detail=Messages.CANNOT_DELETE_SELF_MSG
        )

    try:
        user = await user_crud.delete_user_by_id(user_id, session)
        if not user:
            user_logger.warning(f'Пользователь с ID {user_id} не найден')
            raise HTTPException(
                status_code=Constants.HTTP_404_NOT_FOUND,
                detail=Messages.USER_NOT_FOUND_MSG
            )

        user_logger.info(
            f'Пользователь {user_id} (email: {user.email}) успешно удален '
            f'суперпользователем {current_user.id}'
        )
        return user

    except HTTPException:
        # Перебрасываем HTTP исключения без дополнительного логирования
        raise
    except Exception as e:
        user_logger.error(
            f'Ошибка при удалении пользователя {user_id}: {str(e)}',
            exc_info=True
        )
        raise


@router.post(
    Constants.CHANGE_PASSWORD_PREFIX,
    summary=Descriptions.CHANGE_PASSWORD_SUMMARY,
    description=Descriptions.CHANGE_PASSWORD_DESCRIPTION,
    tags=Constants.USERS_TAGS
)
async def change_password(
    password_data: UserChangePassword,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_user)
):
    '''
    Изменить пароль текущего пользователя.
    Требуется указать текущий пароль для подтверждения.
    '''
    user_logger = logging_config.get_endpoint_logger('user')

    user_logger.info(
        f'Запрос на смену пароля от пользователя {current_user.id} '
        f'(email: {current_user.email})'
    )

    try:
        success = await user_crud.change_password(
            user=current_user,
            old_password=password_data.old_password,
            new_password=password_data.new_password,
            session=session
        )

        if not success:
            user_logger.warning(
                f'Неверный текущий пароль для пользователя {current_user.id}'
            )
            raise HTTPException(
                status_code=Constants.HTTP_400_BAD_REQUEST,
                detail=Messages.INVALID_OLD_PASSWORD_MSG
            )

        user_logger.info(
            f'Пароль успешно изменен для пользователя {current_user.id} '
            f'(email: {current_user.email})'
        )

        return {'message': Messages.PASSWORD_CHANGED_SUCCESS_MSG}

    except HTTPException:
        # Перебрасываем HTTP исключения без дополнительного логирования
        raise
    except Exception as e:
        user_logger.error(
            f'Ошибка при смене пароля для пользователя {current_user.id}: '
            f'{str(e)}',
            exc_info=True
        )
        raise
