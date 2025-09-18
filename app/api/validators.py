from fastapi import Depends, HTTPException

from app.core.user import current_user
from app.core.constants import Constants, Messages
from app.models.user import User


async def current_admin_or_superuser(
    user: User = Depends(current_user)
) -> User:
    '''
    Зависимость для проверки роли администратора ИЛИ суперпользователя.
    Возвращает пользователя, если он является администратором или
    суперпользователем.
    '''
    # Если пользователь суперпользователь, возвращаем его
    if user.is_superuser:
        return user
    # Если пользователь администратор, возвращаем его
    if user.is_administrator:
        return user
    # Если ни то, ни другое, выбрасываем исключение
    raise HTTPException(
        status_code=Constants.HTTP_403_FORBIDDEN,
        detail=Messages.INSUFFICIENT_PERMISSIONS_MSG
    )
