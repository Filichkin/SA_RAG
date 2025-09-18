from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func

from app.core.config import Constants
from app.core.db import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'users'

    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(), onupdate=func.now()
    )
    first_name: Mapped[str] = mapped_column(
        String(length=Constants.STRING_LEN),
        index=False
        )
    last_name: Mapped[str] = mapped_column(
        String(length=Constants.STRING_LEN),
        index=False
        )
    date_of_birth: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
        )
    phone: Mapped[str | None] = mapped_column(
        String(length=Constants.STRING_LEN),
        nullable=False
        )
    is_driver: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
        )
    is_assistant: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
        )
    is_administrator: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
        )

    def __str__(self):
        return f'User(id={self.id!r}, email={self.email!r})'
