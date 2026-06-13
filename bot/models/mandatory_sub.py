from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class MandatorySub(Base):
    """Channels/groups that users must subscribe to."""
    __tablename__ = "mandatory_subs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    chat_title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    invite_link: Mapped[str | None] = mapped_column(String(256), nullable=True)
    language: Mapped[str] = mapped_column(String(8), default="all")  # "all" or specific lang code
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
