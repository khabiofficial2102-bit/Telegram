"""
Check mandatory channel subscriptions.
Bypassed for: /start, /admin, callback queries from sub-check,
and admin user.
"""
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import MandatorySub, User
from bot.locales.i18n import t
from bot.config import ADMIN_ID
from bot.keyboards.sub_keyboard import build_sub_keyboard


# Callbacks that are always allowed
EXEMPT_CALLBACKS = {"check_sub", "lang_"}
# Commands that are always allowed
EXEMPT_COMMANDS = {"/start", "/admin"}


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("user")
        if not user:
            return await handler(event, data)

        # Admin is exempt
        if user.id == ADMIN_ID:
            return await handler(event, data)

        # Exempt certain commands and callbacks
        if isinstance(event, Message):
            text = event.text or ""
            cmd = text.split()[0] if text.startswith("/") else ""
            if cmd in EXEMPT_COMMANDS:
                return await handler(event, data)

        if isinstance(event, CallbackQuery):
            cd = event.data or ""
            if any(cd.startswith(ex) for ex in EXEMPT_CALLBACKS):
                return await handler(event, data)

        session: AsyncSession = data.get("session")
        if not session:
            return await handler(event, data)

        # Load mandatory subs for this user's language + "all"
        result = await session.execute(
            select(MandatorySub).where(
                MandatorySub.language.in_([user.language, "all"])
            )
        )
        subs = result.scalars().all()
        if not subs:
            return await handler(event, data)

        # Check each channel
        from aiogram import Bot
        bot: Bot = data["bot"]
        not_subscribed = []

        for sub in subs:
            try:
                member = await bot.get_chat_member(sub.chat_id, user.id)
                if member.status in ("left", "kicked", "banned"):
                    not_subscribed.append(sub)
            except Exception:
                not_subscribed.append(sub)

        if not not_subscribed:
            return await handler(event, data)

        # Build subscription keyboard
        lang = user.language
        kb = await build_sub_keyboard(not_subscribed, lang)
        msg_text = t("must_subscribe", lang)

        if isinstance(event, Message):
            await event.answer(msg_text, reply_markup=kb)
        elif isinstance(event, CallbackQuery):
            await event.message.answer(msg_text, reply_markup=kb)
            await event.answer()
        return
