"""
Settings module.
- Language change
"""
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User
from bot.locales.i18n import t, LANGUAGE_NAMES
from bot.utils.states import SettingsStates
from bot.services.user_service import UserService
from bot.keyboards.main_keyboard import build_menu_button, build_main_menu_kb

router = Router()


def _lang_settings_kb(current_lang: str) -> InlineKeyboardMarkup:
    buttons = []
    for code, name in LANGUAGE_NAMES.items():
        label = f"✅ {name}" if code == current_lang else name
        buttons.append(
            InlineKeyboardButton(text=label, callback_data=f"set_lang_{code}")
        )
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton(
        text="🏠 Back", callback_data="menu_back_main"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─────────────────────────────────────────────
# Entry points
# ─────────────────────────────────────────────

@router.callback_query(F.data == "menu_settings")
async def cb_settings(cb: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _lang_settings_kb(lang)
    try:
        await cb.message.edit_text(t("settings_lang", lang), reply_markup=kb)
    except Exception:
        await cb.message.answer(t("settings_lang", lang), reply_markup=kb)
    await state.set_state(SettingsStates.choosing_language)
    await cb.answer()


@router.message(Command("settings"))
async def cmd_settings(message: Message, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _lang_settings_kb(lang)
    await message.answer(t("settings_lang", lang), reply_markup=kb)
    await state.set_state(SettingsStates.choosing_language)


# ─────────────────────────────────────────────
# Language selected
# ─────────────────────────────────────────────

@router.callback_query(SettingsStates.choosing_language, F.data.startswith("set_lang_"))
async def cb_set_lang(
    cb: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
):
    new_lang = cb.data.removeprefix("set_lang_")
    if new_lang not in LANGUAGE_NAMES:
        await cb.answer()
        return

    svc = UserService(session)
    await svc.set_language(user.id, new_lang)
    user.language = new_lang

    await state.clear()

    # Update menu button to new language
    menu_kb = build_menu_button(new_lang)
    main_kb  = build_main_menu_kb(new_lang)

    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(
        f"✅ {LANGUAGE_NAMES[new_lang]}",
        reply_markup=menu_kb
    )
    await cb.message.answer(t("main_menu", new_lang), reply_markup=main_kb)
    await cb.answer("✅")
