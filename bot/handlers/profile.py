"""
Profile module.
- Show profile stats
- Edit name
- Edit city
"""
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, Expense, Reminder, DailyPlan
from bot.locales.i18n import t, LANGUAGE_NAMES
from bot.utils.states import ProfileStates
from bot.services.user_service import UserService
from bot.keyboards.main_keyboard import build_back_btn

router = Router()


def _profile_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_edit_name", lang), callback_data="prof_edit_name"),
            InlineKeyboardButton(text=t("btn_edit_city", lang), callback_data="prof_edit_city"),
        ],
        [InlineKeyboardButton(text=t("back_main_btn", lang), callback_data="menu_back_main")],
    ])


async def _build_profile_text(user: User, session: AsyncSession, lang: str) -> str:
    exp_count = (await session.execute(
        select(func.count(Expense.id)).where(Expense.user_id == user.id)
    )).scalar_one()

    rem_count = (await session.execute(
        select(func.count(Reminder.id)).where(
            Reminder.user_id == user.id, Reminder.is_active == True
        )
    )).scalar_one()

    plan_count = (await session.execute(
        select(func.count(DailyPlan.id)).where(
            DailyPlan.user_id == user.id, DailyPlan.is_active == True
        )
    )).scalar_one()

    tariff_key = f"tariff_{user.tariff}"
    tariff_name = t(tariff_key, lang)
    if user.tariff_expires:
        tariff_display = f"{tariff_name} ({t('tariff_expires', lang, date=user.tariff_expires.strftime('%d.%m.%Y'))})"
    else:
        tariff_display = tariff_name

    return t(
        "profile_text", lang,
        name=user.first_name or user.full_name or "—",
        city=user.city or "—",
        lang=LANGUAGE_NAMES.get(lang, lang),
        tariff=tariff_display,
        expenses=exp_count,
        reminders=rem_count,
        plans=plan_count,
    )


# ─────────────────────────────────────────────
# Entry points
# ─────────────────────────────────────────────

@router.callback_query(F.data == "menu_profile")
async def cb_profile(cb: CallbackQuery, user: User, session: AsyncSession, state: FSMContext):
    await state.clear()
    lang = user.language
    text = await _build_profile_text(user, session, lang)
    kb = _profile_keyboard(lang)
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@router.message(Command("profile"))
async def cmd_profile(message: Message, user: User, session: AsyncSession, state: FSMContext):
    await state.clear()
    lang = user.language
    text = await _build_profile_text(user, session, lang)
    kb = _profile_keyboard(lang)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


# ─────────────────────────────────────────────
# Edit name
# ─────────────────────────────────────────────

@router.callback_query(F.data == "prof_edit_name")
async def cb_edit_name(cb: CallbackQuery, user: User, state: FSMContext):
    lang = user.language
    await cb.message.answer(t("enter_new_name", lang))
    await state.set_state(ProfileStates.editing_name)
    await cb.answer()


@router.message(ProfileStates.editing_name, F.text)
async def msg_new_name(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    lang = user.language
    name = message.text.strip()
    if not name or len(name) > 60:
        await message.answer(t("enter_new_name", lang))
        return

    svc = UserService(session)
    await svc.set_name(user.id, name)
    user.first_name = name

    await message.answer(t("profile_updated", lang))
    await state.clear()

    # Refresh profile
    text = await _build_profile_text(user, session, lang)
    kb = _profile_keyboard(lang)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


# ─────────────────────────────────────────────
# Edit city
# ─────────────────────────────────────────────

@router.callback_query(F.data == "prof_edit_city")
async def cb_edit_city(cb: CallbackQuery, user: User, state: FSMContext):
    lang = user.language
    await cb.message.answer(t("enter_new_city", lang))
    await state.set_state(ProfileStates.editing_city)
    await cb.answer()


@router.message(ProfileStates.editing_city, F.text)
async def msg_new_city(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    lang = user.language
    city = message.text.strip()
    if not city or len(city) > 60:
        await message.answer(t("enter_new_city", lang))
        return

    svc = UserService(session)
    await svc.set_city(user.id, city)
    user.city = city

    await message.answer(t("profile_updated", lang))
    await state.clear()

    text = await _build_profile_text(user, session, lang)
    kb = _profile_keyboard(lang)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")
