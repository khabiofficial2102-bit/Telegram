from typing import Any, Awaitable, Callable
import uuid
from datetime import datetime

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, Balance, Referral
from bot.locales.i18n import detect_lang


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session: AsyncSession = data.get("session")

        # session yo'q bo'lsa ham handler ga o'tamiz
        if not session:
            data.setdefault("user", None)
            data.setdefault("is_new_user", False)
            data.setdefault("lang", "uz")
            return await handler(event, data)

        # tg_user ni aniqlash
        tg_user = None
        if isinstance(event, Message):
            tg_user = event.from_user
        elif isinstance(event, CallbackQuery):
            tg_user = event.from_user

        # tg_user yo'q bo'lsa ham handler ga o'tamiz
        if not tg_user:
            data.setdefault("user", None)
            data.setdefault("is_new_user", False)
            data.setdefault("lang", "uz")
            return await handler(event, data)

        try:
            # DB dan userni olish
            result = await session.execute(
                select(User).where(User.id == tg_user.id)
            )
            user = result.scalar_one_or_none()
            is_new = False

            if user:
                # Mavjud userni yangilash
                user.last_active = datetime.utcnow()
                if tg_user.username:
                    user.username = tg_user.username
                await session.commit()

            else:
                # Yangi user yaratish
                is_new = True
                lang = detect_lang(tg_user.language_code)
                referral_code = uuid.uuid4().hex[:10].upper()

                # Referral tekshirish
                referred_by = None
                if isinstance(event, Message) and event.text:
                    if event.text.startswith("/start "):
                        payload = event.text.split(" ", 1)[1].strip()
                        if payload.startswith("ref_"):
                            code = payload[4:]
                            ref_result = await session.execute(
                                select(User).where(User.referral_code == code)
                            )
                            referrer = ref_result.scalar_one_or_none()
                            if referrer and referrer.id != tg_user.id:
                                referred_by = referrer.id

                user = User(
                    id=tg_user.id,
                    username=tg_user.username,
                    full_name=tg_user.full_name,
                    tg_language=tg_user.language_code,
                    language=lang,
                    referral_code=referral_code,
                    referred_by=referred_by,
                )
                session.add(user)

                balance = Balance(user_id=tg_user.id, amount=0.0)
                session.add(balance)
                await session.commit()

                # Referral hisoblash
                if referred_by:
                    ref = Referral(referrer_id=referred_by, referee_id=tg_user.id)
                    session.add(ref)
                    ref_result2 = await session.execute(
                        select(User).where(User.id == referred_by)
                    )
                    referrer_user = ref_result2.scalar_one_or_none()
                    if referrer_user:
                        referrer_user.referral_count += 1
                    await session.commit()

            # inject qilish
            data["user"] = user
            data["is_new_user"] = is_new
            data["lang"] = user.language

        except Exception as e:
            # xato bo'lsa ham bot ishlashda davom etsin
            import logging
            logging.getLogger(__name__).error("UserMiddleware error: %s", e)
            data.setdefault("user", None)
            data.setdefault("is_new_user", False)
            data.setdefault("lang", "uz")

        return await handler(event, data)
