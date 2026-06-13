from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.locales.i18n import t
from bot.models import MandatorySub


async def build_sub_keyboard(subs: list[MandatorySub], lang: str) -> InlineKeyboardMarkup:
    rows = []
    for sub in subs:
        title = sub.chat_title or str(sub.chat_id)
        link = sub.invite_link or f"https://t.me/c/{str(sub.chat_id).lstrip('-100')}"
        rows.append([InlineKeyboardButton(text=f"📢 {title}", url=link)])

    rows.append([
        InlineKeyboardButton(
            text=t("check_sub_btn", lang),
            callback_data="check_sub"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
