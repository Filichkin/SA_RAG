from datetime import datetime

from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func

from app.core.db import Base


class TwoFactorAuthCode(Base):
    """Модель для хранения кодов двухфакторной аутентификации"""
    __tablename__ = 'two_factor_auth_codes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    code: Mapped[str] = mapped_column(
        String(length=6),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    is_used: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
    )

    def __str__(self):
        return (
            f'TwoFactorAuthCode(id={self.id!r}, user_id={self.user_id!r}, '
            f'code={self.code!r})'
        )
