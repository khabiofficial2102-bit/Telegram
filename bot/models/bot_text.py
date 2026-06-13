from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class BotText(Base):
    """
    Editable bot texts stored in DB.
    key examples: "welcome", "offer", "admin_contact", "help",
                  "expense_info", "reminder_info", "currency_info",
                  "plan_info", "weather_info" ...
    """
    __tablename__ = "bot_texts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), index=True)
    language: Mapped[str] = mapped_column(String(8))
    text: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
