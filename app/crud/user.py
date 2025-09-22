from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.password import PasswordHelper

from app.crud.base import CRUDBase
from app.models.user import User


class CRUDUser(CRUDBase):

    def __init__(self, model):
        super().__init__(model)
        self.password_helper = PasswordHelper()

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

    async def change_password(
        self,
        user: User,
        old_password: str,
        new_password: str,
        session: AsyncSession
    ) -> bool:
        '''Сменить пароль пользователя после проверки старого пароля'''
        # Проверяем старый пароль
        if not self.password_helper.verify_and_update(
            old_password, user.hashed_password
        ):
            return False

        # Хешируем новый пароль
        user.hashed_password = self.password_helper.hash(new_password)

        # Увеличиваем версию токена для инвалидации всех существующих токенов
        user.token_version += 1

        # Сохраняем изменения
        await session.commit()
        await session.refresh(user)
        return True

    async def get_by_email(
        self,
        email: str,
        session: AsyncSession
    ) -> Optional[User]:
        '''Получить пользователя по email'''
        return await self.get_by_attribute('email', email, session)

    async def reset_password(
        self,
        user: User,
        new_password: str,
        session: AsyncSession
    ) -> bool:
        '''Сбросить пароль пользователя и обновить версию токена'''
        try:
            # Хешируем новый пароль
            user.hashed_password = self.password_helper.hash(new_password)

            # Увеличиваем версию токена для инвалидации всех существующих
            # токенов
            user.token_version += 1

            # Сохраняем изменения
            await session.commit()
            await session.refresh(user)
            return True
        except Exception:
            await session.rollback()
            return False

    def verify_password(self, password: str, hashed_password: str) -> bool:
        '''Проверить пароль пользователя'''
        return self.password_helper.verify_and_update(
            password, hashed_password
        )[0]

    async def invalidate_user_token(
        self,
        user_id: int,
        session: AsyncSession
    ) -> bool:
        '''Инвалидировать токен пользователя (увеличить версию токена)'''
        try:
            user = await self.get(user_id, session)
            if not user:
                return False

            # Увеличиваем версию токена для инвалидации всех существующих
            # токенов
            user.token_version += 1

            # Сохраняем изменения
            await session.commit()
            await session.refresh(user)
            return True
        except Exception:
            await session.rollback()
            return False


user_crud = CRUDUser(User)
