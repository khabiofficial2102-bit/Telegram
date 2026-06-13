from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.locales.i18n import LANGUAGE_NAMES


def build_lang_keyboard(callback_prefix: str = "lang_") -> InlineKeyboardMarkup:
    """Build 7-language selection keyboard. 2 per row."""
    buttons = [
        InlineKeyboardButton(text=name, callback_data=f"{callback_prefix}{code}")
        for code, name in LANGUAGE_NAMES.items()
    ]
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)
