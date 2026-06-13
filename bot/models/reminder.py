from datetime import datetime
from sqlalchemy import BigInteger, String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    text: Mapped[str] = mapped_column(Text)
    remind_at: Mapped[datetime] = mapped_column(DateTime)   # next fire time
    is_daily: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
