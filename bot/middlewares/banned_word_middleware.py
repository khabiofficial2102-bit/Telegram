"""
Check user messages for banned words.
Warning 1-3 → notify user.
Warning 4 → auto-block.
"""
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import BannedWord, User
from bot.services.user_service import UserService
from bot.locales.i18n import t
from bot.config import MAX_WARNINGS, ADMIN_ID


class BannedWordMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user: User | None = data.get("user")
        if not user:
            return await handler(event, data)

        # Admins are exempt
        from bot.config import ADMIN_ID
        if user.id == ADMIN_ID:
            return await handler(event, data)

        text = event.text or event.caption or ""
        if not text:
            return await handler(event, data)

        session: AsyncSession = data.get("session")
        if not session:
            return await handler(event, data)

        # load banned words (cached per request — fast enough for small list)
        result = await session.execute(select(BannedWord.word))
        banned_words = [row[0].lower() for row in result.fetchall()]

        text_lower = text.lower()
        found = any(w in text_lower for w in banned_words)

        if not found:
            return await handler(event, data)

        # increment warnings
        svc = UserService(session)
        new_count = await svc.increment_warnings(user.id)
        lang = user.language

        if new_count > MAX_WARNINGS:
            # block the user
            await svc.set_blocked(user.id, True)
            await event.answer(t("banned_word_blocked", lang))

            # notify admin
            try:
                from aiogram import Bot
                bot: Bot = data["bot"]
                await bot.send_message(
                    ADMIN_ID,
                    f"🚫 Auto-blocked user <b>{user.id}</b> (@{user.username or '-'}) "
                    f"for banned words.",
                    parse_mode="HTML",
                )
            except Exception:
                pass
            return

        await event.answer(
            t("banned_word_warning", lang, count=new_count, max=MAX_WARNINGS)
        )
        return  # don't pass to handler
