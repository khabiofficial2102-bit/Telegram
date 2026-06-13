from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Subscription(Base):
    """Payment / subscription history."""
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    tariff: Mapped[str] = mapped_column(String(16))         # standard | premium
    period: Mapped[str] = mapped_column(String(8))          # monthly | yearly
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="UZS")
    payment_method: Mapped[str] = mapped_column(String(16)) # stars | card
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending | confirmed | rejected
    discount_applied: Mapped[int] = mapped_column(Integer, default=0)   # %
    receipt_file_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
