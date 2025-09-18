from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import Constants, Messages, Descriptions
from app.core.db import get_async_session
from app.core.user import auth_backend, fastapi_users, current_superuser
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
    users = await user_crud.get_all_users(session, skip=skip, limit=limit)
    return users


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
    # Проверяем, что пользователь не пытается удалить самого себя
    if user_id == current_user.id:
        raise HTTPException(
            status_code=Constants.HTTP_400_BAD_REQUEST,
            detail=Messages.CANNOT_DELETE_SELF_MSG
        )

    user = await user_crud.delete_user_by_id(user_id, session)
    if not user:
        raise HTTPException(
            status_code=Constants.HTTP_404_NOT_FOUND,
            detail=Messages.USER_NOT_FOUND_MSG
        )

    return user
