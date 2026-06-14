"""
/start flow:
1. Language selection (auto-detected + manual choice)
2. Mandatory subscription check
3. Public offer / terms acceptance
4. Welcome message
5. Name + city onboarding (only for new users)
"""
from __future__ import annotations

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.config import ADMIN_USERNAME, DONATION_LINK
from bot.locales.i18n import t, LANGUAGE_NAMES
from bot.models import User, MandatorySub, BotText
from bot.services.user_service import UserService
from bot.keyboards.lang_keyboard import build_lang_keyboard
from bot.keyboards.main_keyboard import build_main_menu_kb, build_menu_button
from bot.keyboards.sub_keyboard import build_sub_keyboard
from bot.utils.states import StartFlow

router = Router()


# ─────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────

async def _get_db_text(session: AsyncSession, key: str, lang: str) -> str | None:
    """Fetch editable text from BotText table, fallback to None."""
    result = await session.execute(
        select(BotText.text).where(BotText.key == key, BotText.language == lang)
    )
    return result.scalar_one_or_none()


async def _get_mandatory_subs(session: AsyncSession, lang: str) -> list[MandatorySub]:
    result = await session.execute(
        select(MandatorySub).where(MandatorySub.language.in_([lang, "all"]))
    )
    return result.scalars().all()


async def _check_subscriptions(bot: Bot, user_id: int, subs: list[MandatorySub]) -> list[MandatorySub]:
    """Return list of subs the user is NOT subscribed to."""
    missing = []
    for sub in subs:
        try:
            member = await bot.get_chat_member(sub.chat_id, user_id)
            if member.status in ("left", "kicked", "banned"):
                missing.append(sub)
        except Exception:
            missing.append(sub)
    return missing


def _offer_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=t("accept_offer_btn", lang),
            callback_data="offer_accept"
        )
    ]])


# ─────────────────────────────────────────────
# /start command
# ─────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
    user: User | None = None,
    lang: str = "uz",
    is_new_user: bool = False,
):
    await state.clear()

    # ── Step 1: Language selection ───────────────────────────────────
    # Always show lang picker first so user can confirm/change
    choose_text = t("choose_language", lang)
    kb = build_lang_keyboard(callback_prefix="start_lang_")

    await message.answer(choose_text, reply_markup=kb)
    await state.set_state(StartFlow.choosing_language)
    await state.update_data(is_new_user=is_new_user)


# ─────────────────────────────────────────────
# Language chosen
# ─────────────────────────────────────────────

@router.callback_query(StartFlow.choosing_language, F.data.startswith("start_lang_"))
async def cb_lang_chosen(
    cb: CallbackQuery,
    state: FSMContext,
    user: User,
    session: AsyncSession,
    bot: Bot,
):
    lang = cb.data.removeprefix("start_lang_")
    svc = UserService(session)
    await svc.set_language(user.id, lang)
    user.language = lang  # update in-memory

    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.answer()

    # ── Step 2: Mandatory subscription ──────────────────────────────
    subs = await _get_mandatory_subs(session, lang)
    if subs:
        missing = await _check_subscriptions(bot, user.id, subs)
        if missing:
            kb = await build_sub_keyboard(missing, lang)
            await cb.message.answer(t("mandatory_sub_text", lang), reply_markup=kb)
            await state.set_state(StartFlow.waiting_sub_check)
            await state.update_data(lang=lang)
            return

    # No mandatory subs → go to offer
    await _show_offer(cb.message, state, session, lang)


# ─────────────────────────────────────────────
# Subscription check button
# ─────────────────────────────────────────────

@router.callback_query(F.data == "check_sub")
async def cb_check_sub(
    cb: CallbackQuery,
    state: FSMContext,
    user: User,
    session: AsyncSession,
    bot: Bot,
):
    lang = user.language
    subs = await _get_mandatory_subs(session, lang)
    missing = await _check_subscriptions(bot, user.id, subs)

    if missing:
        await cb.answer(t("not_subscribed", lang), show_alert=True)
        return

    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.answer("✅")

    current_state = await state.get_state()
    if current_state == StartFlow.waiting_sub_check:
        await _show_offer(cb.message, state, session, lang)
    # else: middleware already handled it, user can continue


# ─────────────────────────────────────────────
# Show offer helper
# ─────────────────────────────────────────────

async def _show_offer(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    lang: str = "uz",
):
    offer_text = await _get_db_text(session, "offer", lang) or t("offer_text", lang)
    kb = _offer_keyboard(lang)
    await message.answer(offer_text, reply_markup=kb, parse_mode="HTML")
    await state.set_state(StartFlow.reading_offer)
    await state.update_data(lang=lang)


# ─────────────────────────────────────────────
# Offer accepted
# ─────────────────────────────────────────────

@router.callback_query(StartFlow.reading_offer, F.data == "offer_accept")
async def cb_offer_accept(
    cb: CallbackQuery,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    lang = user.language
    data = await state.get_data()
    is_new = data.get("is_new_user", False)

    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.answer("✅")

    if is_new and not user.is_onboarded:
        # ── Step 4: Ask name ────────────────────────────────────────
        await cb.message.answer(t("enter_name", lang))
        await state.set_state(StartFlow.entering_name)
    else:
        # Returning user
        await _finish_start(cb.message, state, user, session, lang)


# ─────────────────────────────────────────────
# Enter name (new users)
# ─────────────────────────────────────────────

@router.message(StartFlow.entering_name, F.text)
async def msg_enter_name(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    lang = user.language
    name = message.text.strip()

    if not name or len(name) > 60:
        await message.answer(t("enter_name", lang))
        return

    svc = UserService(session)
    await svc.set_name(user.id, name)
    user.first_name = name

    await message.answer(t("enter_city", lang))
    await state.set_state(StartFlow.entering_city)


# ─────────────────────────────────────────────
# Enter city (new users)
# ─────────────────────────────────────────────

@router.message(StartFlow.entering_city, F.text)
async def msg_enter_city(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    lang = user.language
    city = message.text.strip()

    if not city or len(city) > 60:
        await message.answer(t("enter_city", lang))
        return

    svc = UserService(session)
    await svc.set_city(user.id, city)
    await svc.mark_onboarded(user.id)
    user.city = city
    user.is_onboarded = True

    await message.answer(t("onboard_done", lang))
    await _finish_start(message, state, user, session, lang)


# ─────────────────────────────────────────────
# Finish start flow
# ─────────────────────────────────────────────

async def _finish_start(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
    lang: str = "uz",
):
    """Send welcome + show menu button."""
    await state.clear()

    welcome = await _get_db_text(session, "welcome", lang) or t("welcome_new", lang)
    menu_kb = build_menu_button(lang)

    await message.answer(welcome, reply_markup=menu_kb, parse_mode="HTML")

    # Show main inline menu
    main_kb = build_main_menu_kb(lang)
    await message.answer(t("main_menu", lang), reply_markup=main_kb)


# ─────────────────────────────────────────────
# /offer command (re-show offer anytime)
# ─────────────────────────────────────────────

@router.message(Command("offer"))
async def cmd_offer(
    message: Message,
    user: User,
    session: AsyncSession,
    state: FSMContext,
):
    lang = user.language
    offer_text = await _get_db_text(session, "offer", lang) or t("offer_text", lang)
    await message.answer(offer_text, parse_mode="HTML")


# ─────────────────────────────────────────────
# /help command
# ─────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: Message, user: User | None = None):
    await message.answer(t("help_text", user.language), parse_mode="HTML")
