from fastapi import Depends, HTTPException

from app.core.user import current_administrator, current_superuser
from app.models.user import User


async def current_admin_or_superuser(
    admin_user: User = Depends(current_administrator),
    superuser: User = Depends(current_superuser)
) -> User:
    '''
    Зависимость для проверки роли администратора ИЛИ суперпользователя.
    Возвращает пользователя, если он является администратором или
    суперпользователем.
    '''
    # Если пользователь суперпользователь, возвращаем его
    if superuser.is_superuser:
        return superuser
    # Если пользователь администратор, возвращаем его
    if admin_user.is_administrator:
        return admin_user
    # Если ни то, ни другое, выбрасываем исключение
    raise HTTPException(
        status_code=403,
        detail=(
            'Недостаточно прав. Требуется роль администратора или '
            'суперпользователя.'
        )
    )
