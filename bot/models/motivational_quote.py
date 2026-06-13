from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class MotivationalQuote(Base):
    __tablename__ = "motivational_quotes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(8), default="all")  # "all" or specific lang
    send_time: Mapped[str] = mapped_column(String(8), default="07:00")  # "HH:MM"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
