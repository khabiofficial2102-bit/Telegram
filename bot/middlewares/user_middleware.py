"""
Load (or create) User from DB and inject into handler data.
Also extracts referral code from /start payload.
"""
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.user_service import UserService


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session: AsyncSession = data.get("session")
        if not session:
            return await handler(event, data)

        tg_user = None
        referred_by: int | None = None

        if isinstance(event, Message):
            tg_user = event.from_user
            # check /start ref_XXXXXXXX
            if event.text and event.text.startswith("/start "):
                payload = event.text.split(" ", 1)[1].strip()
                if payload.startswith("ref_"):
                    code = payload[4:]
                    svc = UserService(session)
                    referrer = await svc.get_user_by_referral_code(code)
                    if referrer and referrer.id != (tg_user.id if tg_user else None):
                        referred_by = referrer.id

        elif isinstance(event, CallbackQuery):
            tg_user = event.from_user

        if tg_user:
            svc = UserService(session)
            user, is_new = await svc.get_or_create(
                user_id=tg_user.id,
                username=tg_user.username,
                full_name=tg_user.full_name,
                tg_lang=tg_user.language_code,
                referred_by=referred_by,
            )
            data["user"] = user
            data["user_service"] = svc
            data["is_new_user"] = is_new
            data["lang"] = user.language

        return await handler(event, data)
