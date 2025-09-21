from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.two_factor_auth import TwoFactorAuthCode
from app.api.utils import is_2fa_code_expired


class TwoFactorAuthCRUD:
    """CRUD операции для кодов двухфакторной аутентификации"""

    async def create_code(
        self,
        user_id: int,
        code: str,
        session: AsyncSession
    ) -> TwoFactorAuthCode:
        """
        Создает новый 2FA код для пользователя.

        Args:
            user_id: ID пользователя
            code: 6-значный код
            session: Сессия базы данных

        Returns:
            TwoFactorAuthCode: Созданный код
        """
        # Удаляем все старые коды для этого пользователя
        await self.delete_user_codes(user_id, session)

        # Создаем новый код
        two_fa_code = TwoFactorAuthCode(
            user_id=user_id,
            code=code,
            is_used=False
        )
        session.add(two_fa_code)
        await session.commit()
        await session.refresh(two_fa_code)
        return two_fa_code

    async def get_valid_code(
        self,
        user_id: int,
        code: str,
        session: AsyncSession
    ) -> Optional[TwoFactorAuthCode]:
        """
        Получает валидный 2FA код для пользователя.

        Args:
            user_id: ID пользователя
            code: Код для проверки
            session: Сессия базы данных

        Returns:
            Optional[TwoFactorAuthCode]: Валидный код или None
        """
        stmt = select(TwoFactorAuthCode).where(
            TwoFactorAuthCode.user_id == user_id,
            TwoFactorAuthCode.code == code,
            TwoFactorAuthCode.is_used.is_(False)
        )
        result = await session.execute(stmt)
        two_fa_code = result.scalar_one_or_none()

        if not two_fa_code:
            return None

        # Проверяем, не истек ли код
        if is_2fa_code_expired(two_fa_code.created_at):
            return None

        return two_fa_code

    async def mark_code_as_used(
        self,
        two_fa_code: TwoFactorAuthCode,
        session: AsyncSession
    ) -> None:
        """
        Помечает код как использованный.

        Args:
            two_fa_code: Код для пометки
            session: Сессия базы данных
        """
        two_fa_code.is_used = True
        await session.commit()

    async def delete_user_codes(
        self,
        user_id: int,
        session: AsyncSession
    ) -> None:
        """
        Удаляет все коды пользователя.

        Args:
            user_id: ID пользователя
            session: Сессия базы данных
        """
        stmt = delete(TwoFactorAuthCode).where(
            TwoFactorAuthCode.user_id == user_id
        )
        await session.execute(stmt)
        await session.commit()

    async def cleanup_expired_codes(self, session: AsyncSession) -> None:
        """
        Удаляет все истекшие коды.

        Args:
            session: Сессия базы данных
        """
        # Удаляем коды старше 10 минут
        cutoff_time = datetime.utcnow() - timedelta(minutes=10)
        stmt = delete(TwoFactorAuthCode).where(
            TwoFactorAuthCode.created_at < cutoff_time
        )
        await session.execute(stmt)
        await session.commit()


# Создаем экземпляр CRUD
two_factor_auth_crud = TwoFactorAuthCRUD()
