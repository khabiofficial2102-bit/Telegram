from datetime import datetime
from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    referrer_id: Mapped[int] = mapped_column(BigInteger, index=True)   # who invited
    referee_id: Mapped[int] = mapped_column(BigInteger, unique=True)   # who was invited
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
