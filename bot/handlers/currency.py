"""
Currency converter module.
Input: "100 dollar so'm"  or  "50 EUR UZS"  or  "200 Russia Kazakhstan"
"""
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

from bot.models import User
from bot.locales.i18n import t
from bot.utils.states import CurrencyStates
from bot.services.currency_service import resolve_currency, convert_amount
from bot.keyboards.main_keyboard import build_back_btn

router = Router()


def _currency_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("back_main_btn", lang), callback_data="menu_back_main")
    ]])


# ─────────────────────────────────────────────
# Entry points
# ─────────────────────────────────────────────

@router.callback_query(F.data == "menu_currency")
async def cb_currency_menu(cb: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _currency_keyboard(lang)
    await cb.message.edit_text(t("currency_info", lang), reply_markup=kb, parse_mode="HTML")
    await state.set_state(CurrencyStates.waiting_input)
    await cb.answer()


@router.message(Command("currency"))
async def cmd_currency(message: Message, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _currency_keyboard(lang)
    await message.answer(t("currency_info", lang), reply_markup=kb, parse_mode="HTML")
    await state.set_state(CurrencyStates.waiting_input)


# ─────────────────────────────────────────────
# Process conversion input
# ─────────────────────────────────────────────

@router.message(CurrencyStates.waiting_input, F.text)
async def msg_currency_convert(
    message: Message,
    state: FSMContext,
    user: User,
):
    lang = user.language
    parts = message.text.strip().split(None, 2)

    if len(parts) < 3:
        await message.answer(t("currency_info", lang), parse_mode="HTML")
        return

    # Amount
    try:
        amount = float(parts[0].replace(",", "."))
    except ValueError:
        await message.answer(t("currency_error", lang))
        return

    from_iso = resolve_currency(parts[1])
    to_iso   = resolve_currency(parts[2])

    if not from_iso or not to_iso:
        await message.answer(t("currency_error", lang))
        return

    result = await convert_amount(amount, from_iso, to_iso)
    if result is None:
        await message.answer(t("currency_error", lang))
        return

    await message.answer(
        t("currency_result", lang,
          amount=f"{amount:,.2f}", from_cur=from_iso,
          result=f"{result:,.2f}", to_cur=to_iso),
        parse_mode="HTML",
    )
    # stay in waiting_input so user can convert more
