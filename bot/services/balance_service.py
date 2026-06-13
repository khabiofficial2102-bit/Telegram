"""Balance CRUD & payment helpers."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Balance, BalanceTransaction


class BalanceService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_amount(self, user_id: int) -> float:
        result = await self.session.execute(
            select(Balance.amount).where(Balance.user_id == user_id)
        )
        val = result.scalar_one_or_none()
        if val is None:
            # create row if missing
            bal = Balance(user_id=user_id, amount=0.0)
            self.session.add(bal)
            await self.session.commit()
            return 0.0
        return val

    async def add(self, user_id: int, amount: float, reason: str, note: str | None = None) -> float:
        """Add funds. Returns new balance."""
        bal = await self._get_or_create(user_id)
        bal.amount += amount
        bal.updated_at = datetime.utcnow()

        tx = BalanceTransaction(user_id=user_id, amount=amount, reason=reason, note=note)
        self.session.add(tx)
        await self.session.commit()
        return bal.amount

    async def deduct(self, user_id: int, amount: float, reason: str) -> float | None:
        """Deduct funds. Returns new balance or None if insufficient."""
        bal = await self._get_or_create(user_id)
        if bal.amount < amount:
            return None
        bal.amount -= amount
        bal.updated_at = datetime.utcnow()

        tx = BalanceTransaction(user_id=user_id, amount=-amount, reason=reason)
        self.session.add(tx)
        await self.session.commit()
        return bal.amount

    async def has_enough(self, user_id: int, amount: float) -> bool:
        return await self.get_amount(user_id) >= amount

    async def _get_or_create(self, user_id: int) -> Balance:
        result = await self.session.execute(
            select(Balance).where(Balance.user_id == user_id)
        )
        bal = result.scalar_one_or_none()
        if not bal:
            bal = Balance(user_id=user_id, amount=0.0)
            self.session.add(bal)
            await self.session.flush()
        return bal
