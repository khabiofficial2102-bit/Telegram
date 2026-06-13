"""User CRUD & helpers."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select, func, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, Balance, Referral
from bot.locales.i18n import detect_lang


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------------------------------------------ #
    #  GET / CREATE
    # ------------------------------------------------------------------ #
    async def get(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.username == username.lstrip("@"))
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        user_id: int,
        username: str | None,
        full_name: str | None,
        tg_lang: str | None,
        referred_by: int | None = None,
    ) -> tuple[User, bool]:
        """Return (user, is_new)."""
        user = await self.get(user_id)
        if user:
            # update last_active + username/full_name
            user.last_active = datetime.utcnow()
            if username:
                user.username = username
            if full_name:
                user.full_name = full_name
            await self.session.commit()
            return user, False

        lang = detect_lang(tg_lang)
        referral_code = uuid.uuid4().hex[:10].upper()

        user = User(
            id=user_id,
            username=username,
            full_name=full_name,
            tg_language=tg_lang,
            language=lang,
            referral_code=referral_code,
            referred_by=referred_by,
        )
        self.session.add(user)

        # create balance row
        balance = Balance(user_id=user_id, amount=0.0)
        self.session.add(balance)

        await self.session.commit()

        # handle referral
        if referred_by:
            await self._credit_referral(referred_by, user_id)

        return user, True

    # ------------------------------------------------------------------ #
    #  UPDATE helpers
    # ------------------------------------------------------------------ #
    async def set_language(self, user_id: int, lang: str) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(language=lang)
        )
        await self.session.commit()

    async def set_name(self, user_id: int, name: str) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(first_name=name)
        )
        await self.session.commit()

    async def set_city(self, user_id: int, city: str) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(city=city)
        )
        await self.session.commit()

    async def mark_onboarded(self, user_id: int) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(is_onboarded=True)
        )
        await self.session.commit()

    async def set_blocked(self, user_id: int, blocked: bool) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(is_blocked=blocked)
        )
        await self.session.commit()

    async def increment_warnings(self, user_id: int) -> int:
        """Increment warnings counter. Returns new count."""
        user = await self.get(user_id)
        if not user:
            return 0
        user.warnings += 1
        await self.session.commit()
        return user.warnings

    async def reset_warnings(self, user_id: int) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(warnings=0)
        )
        await self.session.commit()

    async def set_tariff(self, user_id: int, tariff: str, expires: datetime | None) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(
                tariff=tariff, tariff_expires=expires
            )
        )
        await self.session.commit()

    async def increment_ai_free(self, user_id: int) -> int:
        user = await self.get(user_id)
        if not user:
            return 0
        user.ai_free_used += 1
        await self.session.commit()
        return user.ai_free_used

    # ------------------------------------------------------------------ #
    #  STATS
    # ------------------------------------------------------------------ #
    async def total_count(self) -> int:
        result = await self.session.execute(select(func.count(User.id)))
        return result.scalar_one()

    async def active_count(self, days: int = 30) -> int:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            select(func.count(User.id)).where(User.last_active >= cutoff)
        )
        return result.scalar_one()

    async def blocked_count(self) -> int:
        result = await self.session.execute(
            select(func.count(User.id)).where(User.is_blocked == True)
        )
        return result.scalar_one()

    async def today_count(self) -> int:
        today = datetime.utcnow().date()
        result = await self.session.execute(
            select(func.count(User.id)).where(
                func.date(User.created_at) == today
            )
        )
        return result.scalar_one()

    async def monthly_count(self) -> int:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=30)
        result = await self.session.execute(
            select(func.count(User.id)).where(User.created_at >= cutoff)
        )
        return result.scalar_one()

    async def lang_stats(self) -> dict[str, int]:
        result = await self.session.execute(
            select(User.language, func.count(User.id))
            .group_by(User.language)
        )
        return {row[0]: row[1] for row in result.fetchall()}

    async def city_stats(self, limit: int = 10) -> list[tuple[str, int]]:
        result = await self.session.execute(
            select(User.city, func.count(User.id))
            .where(User.city.isnot(None))
            .group_by(User.city)
            .order_by(func.count(User.id).desc())
            .limit(limit)
        )
        return result.fetchall()

    async def all_ids(self) -> list[int]:
        result = await self.session.execute(select(User.id))
        return [row[0] for row in result.fetchall()]

    async def all_ids_by_lang(self, lang: str) -> list[int]:
        result = await self.session.execute(
            select(User.id).where(User.language == lang, User.is_blocked == False)
        )
        return [row[0] for row in result.fetchall()]

    async def all_active_ids(self) -> list[int]:
        result = await self.session.execute(
            select(User.id).where(User.is_blocked == False)
        )
        return [row[0] for row in result.fetchall()]

    async def all_users_info(self) -> list[User]:
        result = await self.session.execute(select(User).order_by(User.created_at.desc()))
        return result.scalars().all()

    # ------------------------------------------------------------------ #
    #  REFERRAL
    # ------------------------------------------------------------------ #
    async def _credit_referral(self, referrer_id: int, referee_id: int) -> None:
        # prevent duplicate
        existing = await self.session.execute(
            select(Referral).where(Referral.referee_id == referee_id)
        )
        if existing.scalar_one_or_none():
            return

        ref = Referral(referrer_id=referrer_id, referee_id=referee_id)
        self.session.add(ref)

        # increment referrer's count
        referrer = await self.get(referrer_id)
        if referrer:
            referrer.referral_count += 1
        await self.session.commit()

    async def get_referral_count(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Referral.id)).where(Referral.referrer_id == user_id)
        )
        return result.scalar_one()

    async def get_user_by_referral_code(self, code: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.referral_code == code)
        )
        return result.scalar_one_or_none()
