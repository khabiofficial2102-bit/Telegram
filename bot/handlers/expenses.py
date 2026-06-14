"""
Expenses module.
- Add expense: "amount currency description"
- Reports: today / week / month / year
- Convert total to any currency
- Clear all
"""
from __future__ import annotations

import re
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, Expense
from bot.locales.i18n import t
from bot.utils.states import ExpenseStates
from bot.utils.helpers import period_range
from bot.keyboards.main_keyboard import build_back_btn, build_confirm_kb
from bot.services.currency_service import resolve_currency, convert_amount

router = Router()

# ── Currency alias map (name/country → ISO code) lives in currency_service ──

def _expenses_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text=t("btn_today", lang),  callback_data="exp_report_today"),
            InlineKeyboardButton(text=t("btn_week",  lang),  callback_data="exp_report_week"),
        ],
        [
            InlineKeyboardButton(text=t("btn_month", lang),  callback_data="exp_report_month"),
            InlineKeyboardButton(text=t("btn_year",  lang),  callback_data="exp_report_year"),
        ],
        [
            InlineKeyboardButton(text=t("btn_convert", lang), callback_data="exp_convert"),
        ],
        [
            InlineKeyboardButton(text=t("btn_clear_expenses", lang), callback_data="exp_clear"),
        ],
        [
            InlineKeyboardButton(text=t("back_main_btn", lang), callback_data="menu_back_main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _show_expenses_menu(target, lang: str):
    kb = _expenses_keyboard(lang)
    info = t("expenses_info", lang)
    if isinstance(target, Message):
        await target.answer(info, reply_markup=kb, parse_mode="HTML")
    else:
        try:
            await target.message.edit_text(info, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await target.message.answer(info, reply_markup=kb, parse_mode="HTML")


# ─────────────────────────────────────────────
# Entry points
# ─────────────────────────────────────────────

@router.callback_query(F.data == "menu_expenses")
async def cb_expenses_menu(cb: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    await state.set_state(ExpenseStates.adding)
    await _show_expenses_menu(cb, user.language)
    await cb.answer()


@router.message(Command("expenses"))
async def cmd_expenses(message: Message, user: User, state: FSMContext):
    await state.clear()
    await state.set_state(ExpenseStates.adding)
    await _show_expenses_menu(message, user.language)


# ─────────────────────────────────────────────
# Add expense (free-text while in adding state)
# ─────────────────────────────────────────────

@router.message(ExpenseStates.adding, F.text)
async def msg_add_expense(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    lang = user.language
    text = message.text.strip()

    # Parse: first token = amount, second = currency, rest = description
    parts = text.split(None, 2)
    if len(parts) < 2:
        await message.answer(t("expense_invalid", lang))
        return

    # Amount
    amount_raw = parts[0].replace(",", ".")
    try:
        amount = float(amount_raw)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer(t("expense_invalid", lang))
        return

    currency_raw = parts[1]
    description  = parts[2].strip() if len(parts) > 2 else "—"

    iso = resolve_currency(currency_raw)
    if not iso:
        await message.answer(t("currency_error", lang))
        return

    expense = Expense(
        user_id=user.id,
        amount=amount,
        currency=iso,
        currency_raw=currency_raw,
        description=description,
        created_at=datetime.utcnow(),
    )
    session.add(expense)
    await session.commit()

    await message.answer(
        t("expense_added", lang, amount=amount, currency=iso, desc=description),
        parse_mode="HTML",
    )
    # stay in adding state — user can add more


# ─────────────────────────────────────────────
# Reports
# ─────────────────────────────────────────────

async def _send_report(
    cb: CallbackQuery,
    session: AsyncSession,
    user: User,
    period: str,
):
    lang = user.language
    start, end = period_range(period)

    result = await session.execute(
        select(Expense).where(
            Expense.user_id == user.id,
            Expense.created_at >= start,
            Expense.created_at < end,
        ).order_by(Expense.created_at.desc())
    )
    expenses = result.scalars().all()

    if not expenses:
        await cb.answer(t("expense_report_empty", lang), show_alert=True)
        return

    period_label = t(f"period_{period}", lang)
    lines = [t("expense_report_title", lang, period=period_label)]

    # Group by currency
    totals: dict[str, float] = {}
    for exp in expenses:
        lines.append(f"• {exp.amount:,.2f} {exp.currency} — {exp.description}")
        totals[exp.currency] = totals.get(exp.currency, 0) + exp.amount

    lines.append("")
    for cur, total in totals.items():
        lines.append(t("expense_report_total", lang, total=f"{total:,.2f}", currency=cur))

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("back_btn", lang), callback_data="menu_expenses")
    ]])
    await cb.message.answer("\n".join(lines), reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "exp_report_today")
async def cb_report_today(cb: CallbackQuery, user: User, session: AsyncSession):
    await _send_report(cb, session, user, "today")

@router.callback_query(F.data == "exp_report_week")
async def cb_report_week(cb: CallbackQuery, user: User, session: AsyncSession):
    await _send_report(cb, session, user, "week")

@router.callback_query(F.data == "exp_report_month")
async def cb_report_month(cb: CallbackQuery, user: User, session: AsyncSession):
    await _send_report(cb, session, user, "month")

@router.callback_query(F.data == "exp_report_year")
async def cb_report_year(cb: CallbackQuery, user: User, session: AsyncSession):
    await _send_report(cb, session, user, "year")


# ─────────────────────────────────────────────
# Convert total
# ─────────────────────────────────────────────

@router.callback_query(F.data == "exp_convert")
async def cb_exp_convert(cb: CallbackQuery, user: User, state: FSMContext):
    lang = user.language
    await cb.message.answer(t("expense_convert_ask", lang))
    await state.set_state(ExpenseStates.converting)
    await cb.answer()


@router.message(ExpenseStates.converting, F.text)
async def msg_exp_convert(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    lang = user.language
    target_iso = resolve_currency(message.text.strip())
    if not target_iso:
        await message.answer(t("currency_error", lang))
        return

    # Sum all expenses in their original currencies, convert to target
    result = await session.execute(
        select(Expense).where(Expense.user_id == user.id)
    )
    expenses = result.scalars().all()

    if not expenses:
        await message.answer(t("expense_report_empty", lang))
        await state.set_state(ExpenseStates.adding)
        return

    total = 0.0
    for exp in expenses:
        converted = await convert_amount(exp.amount, exp.currency, target_iso)
        if converted is not None:
            total += converted

    await message.answer(
        t("expense_convert_result", lang, amount=f"{total:,.2f}", currency=target_iso),
        parse_mode="HTML",
    )
    await state.set_state(ExpenseStates.adding)


# ─────────────────────────────────────────────
# Clear
# ─────────────────────────────────────────────

@router.callback_query(F.data == "exp_clear")
async def cb_exp_clear(cb: CallbackQuery, user: User | None = None):
    lang = user.language
    kb = build_confirm_kb(lang, confirm_cb="exp_clear_confirm", cancel_cb="menu_expenses")
    await cb.message.answer(t("clear_confirm", lang), reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data == "exp_clear_confirm")
async def cb_exp_clear_confirm(
    cb: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
):
    lang = user.language
    await session.execute(delete(Expense).where(Expense.user_id == user.id))
    await session.commit()
    await cb.message.edit_text(t("cleared_success", lang))
    await state.set_state(ExpenseStates.adding)
    await cb.answer()
