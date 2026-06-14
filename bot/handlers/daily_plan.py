"""
Daily plan module.
Input: "HH:MM plan text"
Reminder-like: fires at that time every day.
"""
from __future__ import annotations

from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, DailyPlan
from bot.locales.i18n import t
from bot.utils.states import DailyPlanStates
from bot.keyboards.main_keyboard import build_confirm_kb

router = Router()


def _plan_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_list_plans",  lang), callback_data="plan_list"),
            InlineKeyboardButton(text=t("btn_clear_plans", lang), callback_data="plan_clear"),
        ],
        [InlineKeyboardButton(text=t("back_main_btn", lang), callback_data="menu_back_main")],
    ])


# ─────────────────────────────────────────────
# Entry points
# ─────────────────────────────────────────────

@router.callback_query(F.data == "menu_daily_plan")
async def cb_plan_menu(cb: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _plan_keyboard(lang)
    await cb.message.edit_text(t("plan_info", lang), reply_markup=kb, parse_mode="HTML")
    await state.set_state(DailyPlanStates.adding)
    await cb.answer()


@router.message(Command("plans"))
async def cmd_plans(message: Message, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _plan_keyboard(lang)
    await message.answer(t("plan_info", lang), reply_markup=kb, parse_mode="HTML")
    await state.set_state(DailyPlanStates.adding)


# ─────────────────────────────────────────────
# Add plan
# ─────────────────────────────────────────────

@router.message(DailyPlanStates.adding, F.text)
async def msg_add_plan(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    lang = user.language
    raw = message.text.strip()

    # Parse "HH:MM text"
    import re
    m = re.match(r"^(\d{1,2}:\d{2})\s+(.+)$", raw, re.DOTALL)
    if not m:
        await message.answer(t("plan_invalid", lang))
        return

    time_str = m.group(1)
    text     = m.group(2).strip()

    # Validate time
    try:
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        await message.answer(t("plan_invalid", lang))
        return

    plan = DailyPlan(
        user_id=user.id,
        text=text,
        send_time=time_str,
        is_active=True,
    )
    session.add(plan)
    await session.commit()

    await message.answer(
        t("plan_added", lang, time=time_str, text=text),
        parse_mode="HTML",
    )
    # Stay in adding state


# ─────────────────────────────────────────────
# List plans
# ─────────────────────────────────────────────

@router.callback_query(F.data == "plan_list")
async def cb_plan_list(cb: CallbackQuery, user: User, session: AsyncSession):
    lang = user.language
    result = await session.execute(
        select(DailyPlan).where(
            DailyPlan.user_id == user.id,
            DailyPlan.is_active == True,
        ).order_by(DailyPlan.send_time)
    )
    plans = result.scalars().all()

    if not plans:
        await cb.answer(t("plans_empty", lang), show_alert=True)
        return

    lines = ["📅 <b>Kunlik rejalar:</b>\n"]
    for p in plans:
        time_display = p.send_time or "—"
        lines.append(f"🕐 <b>{time_display}</b> — {p.text}")

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("back_btn", lang), callback_data="menu_daily_plan")
    ]])
    await cb.message.answer("\n".join(lines), reply_markup=kb, parse_mode="HTML")
    await cb.answer()


# ─────────────────────────────────────────────
# Clear plans
# ─────────────────────────────────────────────

@router.callback_query(F.data == "plan_clear")
async def cb_plan_clear(cb: CallbackQuery, user: User | None = None):
    lang = user.language
    kb = build_confirm_kb(lang, "plan_clear_confirm", "menu_daily_plan")
    await cb.message.answer(t("clear_confirm", lang), reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data == "plan_clear_confirm")
async def cb_plan_clear_confirm(
    cb: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
):
    lang = user.language
    await session.execute(delete(DailyPlan).where(DailyPlan.user_id == user.id))
    await session.commit()
    await cb.message.edit_text(t("plans_cleared", lang))
    await state.set_state(DailyPlanStates.adding)
    await cb.answer()
