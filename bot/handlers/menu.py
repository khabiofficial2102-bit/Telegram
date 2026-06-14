"""
Main menu handler.
- "Menu" reply button → show inline main menu
- /menu command → same
- menu_* callbacks → dispatch to sub-sections
- menu_back_main → return to main menu
"""
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.models import User
from bot.locales.i18n import t
from bot.keyboards.main_keyboard import build_main_menu_kb, build_menu_button

router = Router()


# ─────────────────────────────────────────────
# "Menu" reply button or /menu command
# ─────────────────────────────────────────────

@router.message(Command("menu"))
async def cmd_menu(message: Message, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = build_main_menu_kb(lang)
    await message.answer(t("main_menu", lang), reply_markup=kb)


@router.message(F.text == "📋 Menu")
@router.message(F.text == "📋 Меню")
@router.message(F.text == "📋 Menü")
@router.message(F.text == "📋 Menú")
@router.message(F.text == "📋 القائمة")
@router.message(F.text == "📋 मेनू")
async def reply_menu_btn(message: Message, user: User, state: FSMContext):
    """Catch the persistent 'Menu' reply-keyboard button in any language."""
    await state.clear()
    lang = user.language
    kb = build_main_menu_kb(lang)
    await message.answer(t("main_menu", lang), reply_markup=kb)


@router.message(F.text.startswith("📋"))
async def reply_menu_btn_fallback(message: Message, user: User, state: FSMContext):
    """Catch any variation of the menu button (e.g. if text includes lang name)."""
    lang = user.language
    menu_text = t("menu_btn", lang)
    if message.text and message.text.strip() == menu_text:
        await state.clear()
        kb = build_main_menu_kb(lang)
        await message.answer(t("main_menu", lang), reply_markup=kb)


# ─────────────────────────────────────────────
# Back to main menu (inline)
# ─────────────────────────────────────────────

@router.callback_query(F.data == "menu_back_main")
async def cb_back_main(cb: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = build_main_menu_kb(lang)
    try:
        await cb.message.edit_text(t("main_menu", lang), reply_markup=kb)
    except Exception:
        await cb.message.answer(t("main_menu", lang), reply_markup=kb)
    await cb.answer()


# ─────────────────────────────────────────────
# menu_* dispatch callbacks
# Each sub-section handler registers its own callback, but if somehow
# a menu_X callback arrives here it means no module claimed it yet.
# ─────────────────────────────────────────────

SECTION_COMMANDS = {
    "expenses":     "expenses",
    "reminders":    "reminders",
    "currency":     "currency",
    "daily_plan":   "plans",
    "weather":      "weather",
    "profile":      "profile",
    "ai":           "ai",
    "balance":      "balance",
    "tariff":       "tariff",
    "referral":     "referral",
    "settings":     "settings",
    "admin_contact":"admin_contact",
}


@router.callback_query(F.data.startswith("menu_"))
async def cb_menu_dispatch(cb: CallbackQuery, user: User | None = None):
    """Fallback: echo which section was tapped (real handlers registered elsewhere)."""
    section = cb.data.removeprefix("menu_")
    if section not in SECTION_COMMANDS:
        await cb.answer()
        return
    # Each handler already listens for menu_{section} — this won't fire if they're registered.
    await cb.answer()
