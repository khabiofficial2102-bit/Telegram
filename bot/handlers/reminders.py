"""
Reminders module.
- Add reminder: "YYYY-MM-DD HH:MM text" or "HH:MM text" (today)
- Choose one-time or daily
- List reminders
- Clear all
"""
from __future__ import annotations

from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, Reminder
from bot.locales.i18n import t
from bot.utils.states import ReminderStates
from bot.utils.helpers import parse_datetime_text
from bot.keyboards.main_keyboard import build_back_btn, build_confirm_kb

router = Router()


def _reminders_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_list_reminders", lang),  callback_data="rem_list"),
            InlineKeyboardButton(text=t("btn_clear_reminders", lang), callback_data="rem_clear"),
        ],
        [InlineKeyboardButton(text=t("back_main_btn", lang), callback_data="menu_back_main")],
    ])


def _repeat_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("btn_once",  lang), callback_data="rem_once"),
        InlineKeyboardButton(text=t("btn_daily", lang), callback_data="rem_daily"),
    ]])


# ─────────────────────────────────────────────
# Entry points
# ─────────────────────────────────────────────

@router.callback_query(F.data == "menu_reminders")
async def cb_reminders_menu(cb: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _reminders_keyboard(lang)
    await cb.message.edit_text(t("reminders_info", lang), reply_markup=kb, parse_mode="HTML")
    await state.set_state(ReminderStates.adding_text)
    await cb.answer()


@router.message(Command("reminders"))
async def cmd_reminders(message: Message, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _reminders_keyboard(lang)
    await message.answer(t("reminders_info", lang), reply_markup=kb, parse_mode="HTML")
    await state.set_state(ReminderStates.adding_text)


# ─────────────────────────────────────────────
# Parse reminder text
# ─────────────────────────────────────────────

@router.message(ReminderStates.adding_text, F.text)
async def msg_reminder_text(message: Message, state: FSMContext, user: User | None = None):
    lang = user.language
    dt, text = parse_datetime_text(message.text.strip())

    if dt is None or not text:
        await message.answer(t("reminder_invalid", lang))
        return

    if dt < datetime.utcnow():
        # past time → skip same logic, still allow for "today" if in future by tz offset
        # just add 1 day if already passed today
        if (dt + timedelta(days=1)) > datetime.utcnow():
            dt = dt + timedelta(days=1)

    await state.update_data(remind_dt=dt.isoformat(), remind_text=text)
    kb = _repeat_keyboard(lang)
    await message.answer(t("reminder_ask_repeat", lang), reply_markup=kb)
    await state.set_state(ReminderStates.choosing_repeat)


# ─────────────────────────────────────────────
# Repeat choice
# ─────────────────────────────────────────────

async def _save_reminder(
    cb: CallbackQuery,
    state: FSMContext,
    user: User,
    session: AsyncSession,
    is_daily: bool,
):
    lang = user.language
    data = await state.get_data()
    dt   = datetime.fromisoformat(data["remind_dt"])
    text = data["remind_text"]

    reminder = Reminder(
        user_id=user.id,
        text=text,
        remind_at=dt,
        is_daily=is_daily,
        is_active=True,
    )
    session.add(reminder)
    await session.commit()

    time_str = dt.strftime("%Y-%m-%d %H:%M")
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(
        t("reminder_added", lang, time=time_str, text=text),
        parse_mode="HTML",
    )
    await state.set_state(ReminderStates.adding_text)
    await cb.answer()


@router.callback_query(ReminderStates.choosing_repeat, F.data == "rem_once")
async def cb_rem_once(cb: CallbackQuery, state: FSMContext, user: User, session: AsyncSession):
    await _save_reminder(cb, state, user, session, is_daily=False)


@router.callback_query(ReminderStates.choosing_repeat, F.data == "rem_daily")
async def cb_rem_daily(cb: CallbackQuery, state: FSMContext, user: User, session: AsyncSession):
    await _save_reminder(cb, state, user, session, is_daily=True)


# ─────────────────────────────────────────────
# List reminders
# ─────────────────────────────────────────────

@router.callback_query(F.data == "rem_list")
async def cb_rem_list(cb: CallbackQuery, user: User, session: AsyncSession):
    lang = user.language
    result = await session.execute(
        select(Reminder).where(
            Reminder.user_id == user.id,
            Reminder.is_active == True,
        ).order_by(Reminder.remind_at)
    )
    reminders = result.scalars().all()

    if not reminders:
        await cb.answer(t("reminders_empty", lang), show_alert=True)
        return

    lines = ["📋 <b>Eslatmalar:</b>\n"]
    for rem in reminders:
        repeat = "🔁" if rem.is_daily else "1️⃣"
        lines.append(f"{repeat} <b>{rem.remind_at.strftime('%Y-%m-%d %H:%M')}</b> — {rem.text}")

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("back_btn", lang), callback_data="menu_reminders")
    ]])
    await cb.message.answer("\n".join(lines), reply_markup=kb, parse_mode="HTML")
    await cb.answer()


# ─────────────────────────────────────────────
# Clear reminders
# ─────────────────────────────────────────────

@router.callback_query(F.data == "rem_clear")
async def cb_rem_clear(cb: CallbackQuery, user: User | None = None):
    lang = user.language
    kb = build_confirm_kb(lang, "rem_clear_confirm", "menu_reminders")
    await cb.message.answer(t("clear_confirm", lang), reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data == "rem_clear_confirm")
async def cb_rem_clear_confirm(
    cb: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
):
    lang = user.language
    await session.execute(delete(Reminder).where(Reminder.user_id == user.id))
    await session.commit()
    await cb.message.edit_text(t("reminders_cleared", lang))
    await state.set_state(ReminderStates.adding_text)
    await cb.answer()
