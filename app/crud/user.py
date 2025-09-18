from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user import User


class CRUDUser(CRUDBase):

    async def get_all_users(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        '''Получить всех пользователей с пагинацией'''
        result = await session.execute(
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.created.desc())
        )
        return result.scalars().all()

    async def delete_user_by_id(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Optional[User]:
        '''Удалить пользователя по ID'''
        user = await self.get(user_id, session)
        if user:
            await self.remove(user, session)
        return user


user_crud = CRUDUser(User)
