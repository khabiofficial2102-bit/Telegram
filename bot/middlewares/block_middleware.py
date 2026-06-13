"""Block blocked users from using the bot."""
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from bot.locales.i18n import t
from bot.config import ADMIN_USERNAME
from bot.models import User


class BlockMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("user")
        if user and user.is_blocked:
            lang = getattr(user, "language", "uz")
            msg = t("blocked_msg", lang, admin_username=ADMIN_USERNAME)

            if isinstance(event, Message):
                await event.answer(msg)
            elif isinstance(event, CallbackQuery):
                await event.answer(msg, show_alert=True)
            return  # stop processing

        return await handler(event, data)
