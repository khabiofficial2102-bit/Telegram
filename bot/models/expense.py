from datetime import datetime
from sqlalchemy import BigInteger, String, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8))        # normalized ISO code e.g. "UZS"
    currency_raw: Mapped[str] = mapped_column(String(32))   # what user typed
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
