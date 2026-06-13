from datetime import datetime
from sqlalchemy import BigInteger, Float, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Balance(Base):
    __tablename__ = "balances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0)   # UZS
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BalanceTransaction(Base):
    __tablename__ = "balance_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    amount: Mapped[float] = mapped_column(Float)        # positive = credit, negative = debit
    reason: Mapped[str] = mapped_column(String(64))     # "topup_card" | "topup_stars" | "ai_use" | ...
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
