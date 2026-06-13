from datetime import datetime, time
from sqlalchemy import BigInteger, String, Boolean, DateTime, Text, Time
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class DailyPlan(Base):
    __tablename__ = "daily_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    text: Mapped[str] = mapped_column(Text)
    send_time: Mapped[str | None] = mapped_column(String(8), nullable=True)   # "HH:MM"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
