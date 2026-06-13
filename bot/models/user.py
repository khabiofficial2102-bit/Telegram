from datetime import datetime
from sqlalchemy import BigInteger, String, Boolean, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)          # Telegram user_id
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)  # user-entered name
    city: Mapped[str | None] = mapped_column(String(64), nullable=True)

    language: Mapped[str] = mapped_column(String(8), default="uz")
    tg_language: Mapped[str | None] = mapped_column(String(8), nullable=True)  # detected from Telegram

    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_onboarded: Mapped[bool] = mapped_column(Boolean, default=False)  # completed name+city step
    warnings: Mapped[int] = mapped_column(Integer, default=0)

    tariff: Mapped[str] = mapped_column(String(16), default="free")  # free | standard | premium
    tariff_expires: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    referral_code: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    referred_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    referral_count: Mapped[int] = mapped_column(Integer, default=0)

    # Pending referral discounts (saved for future use)
    pending_standard_discount: Mapped[int] = mapped_column(Integer, default=0)  # %
    pending_premium_discount: Mapped[int] = mapped_column(Integer, default=0)   # %

    # AI free usage tracking
    ai_free_used: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_active: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User id={self.id} lang={self.language} tariff={self.tariff}>"
