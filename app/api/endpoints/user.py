from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Constants
from app.core.db import get_async_session
from app.core.user import auth_backend, fastapi_users
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.api.validators import current_admin_or_superuser


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
    '/all',
    response_model=List[UserRead],
    summary='Получить всех пользователей',
    description=(
        'Получить список всех пользователей. Доступно только '
        'администраторам и суперпользователям.'
    )
)
async def get_all_users(
    skip: int = Query(0, ge=0, description='Количество записей для пропуска'),
    limit: int = Query(
        100, ge=1, le=1000, description='Максимальное количество записей'
    ),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_admin_or_superuser)
):
    '''
    Получить всех пользователей с пагинацией.
    Доступно только пользователям с ролью администратора или суперпользователя.
    '''
    users = await user_crud.get_all_users(session, skip=skip, limit=limit)
    return users


@router.delete(
    '/{user_id}',
    response_model=UserRead,
    summary='Удалить пользователя',
    description=(
        'Удалить пользователя по ID. Доступно только администраторам и '
        'суперпользователям.'
    )
)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_admin_or_superuser)
):
    '''
    Удалить пользователя по ID.
    Доступно только пользователям с ролью администратора или суперпользователя.
    '''
    # Проверяем, что пользователь не пытается удалить самого себя
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail='Нельзя удалить самого себя'
        )

    user = await user_crud.delete_user_by_id(user_id, session)
    if not user:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не найден'
        )

    return user
