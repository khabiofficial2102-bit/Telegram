from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    BotCommand,
)
from bot.locales.i18n import t


def build_menu_button(lang: str) -> ReplyKeyboardMarkup:
    """Single blue 'Menu' button pinned at bottom-left."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("menu_btn", lang))]],
        resize_keyboard=True,
        persistent=True,
    )


def build_main_menu_kb(lang: str) -> InlineKeyboardMarkup:
    """Main inline menu grid."""
    buttons_def = [
        ("btn_expenses",       "expenses"),
        ("btn_reminders",      "reminders"),
        ("btn_currency",       "currency"),
        ("btn_daily_plan",     "daily_plan"),
        ("btn_weather",        "weather"),
        ("btn_profile",        "profile"),
        ("btn_ai",             "ai"),
        ("btn_balance",        "balance"),
        ("btn_tariff",         "tariff"),
        ("btn_referral",       "referral"),
        ("btn_settings",       "settings"),
        ("btn_admin_contact",  "admin_contact"),
    ]

    buttons = [
        InlineKeyboardButton(text=t(key, lang), callback_data=f"menu_{cb}")
        for key, cb in buttons_def
    ]
    # 2 columns
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_back_btn(lang: str, target: str = "main") -> InlineKeyboardMarkup:
    """Single back button."""
    if target == "main":
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=t("back_main_btn", lang),
                callback_data="menu_back_main"
            )
        ]])
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=t("back_btn", lang),
            callback_data=f"back_{target}"
        )
    ]])


def build_confirm_kb(lang: str, confirm_cb: str, cancel_cb: str = "cancel") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("btn_confirm", lang), callback_data=confirm_cb),
        InlineKeyboardButton(text=t("btn_cancel", lang),  callback_data=cancel_cb),
    ]])


BOT_COMMANDS = [
    BotCommand(command="start",    description="Botni boshlash / Start"),
    BotCommand(command="menu",     description="Asosiy menyu"),
    BotCommand(command="profile",  description="Profilim"),
    BotCommand(command="offer",    description="Foydalanish shartlari"),
    BotCommand(command="settings", description="Sozlamalar"),
    BotCommand(command="help",     description="Yordam"),
    BotCommand(command="balance",  description="Balans"),
    BotCommand(command="tariff",   description="Tariflar"),
    BotCommand(command="referral", description="Referal"),
    BotCommand(command="ai",       description="AI Yordamchi"),
    BotCommand(command="expenses", description="Xarajatlar"),
    BotCommand(command="reminders",description="Eslatmalar"),
    BotCommand(command="plans",    description="Kunlik reja"),
    BotCommand(command="weather",  description="Ob-havo"),
    BotCommand(command="currency", description="Valyuta"),
]
