from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class ScheduledAd(Base):
    __tablename__ = "scheduled_ads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    language: Mapped[str] = mapped_column(String(8), default="all")  # "all" or specific lang
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_file_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_type: Mapped[str | None] = mapped_column(String(16), nullable=True)  # photo | video
    send_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # None = immediate
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
