"""
Referral module.
- Show referral link
- Show referral count + discount status
- Discount carry-over logic is handled in tariff.py
"""
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User
from bot.locales.i18n import t
from bot.services.user_service import UserService
from bot.config import REFERRAL_DISCOUNTS

router = Router()


async def _referral_text(user: User, session: AsyncSession, lang: str, bot_username: str) -> str:
    svc = UserService(session)
    count = await svc.get_referral_count(user.id)
    link = f"https://t.me/{bot_username}?start=ref_{user.referral_code}"
    return t("referral_info", lang, link=link, count=count)


@router.callback_query(F.data == "menu_referral")
async def cb_referral(cb: CallbackQuery, user: User, session: AsyncSession):
    lang = user.language
    bot_info = await cb.bot.get_me()
    text = await _referral_text(user, session, lang, bot_info.username)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("back_main_btn", lang), callback_data="menu_back_main")
    ]])
    try:
        await cb.message.edit_text(text, reply_markup=kb,
                                   parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        await cb.message.answer(text, reply_markup=kb,
                                parse_mode="HTML", disable_web_page_preview=True)
    await cb.answer()


@router.message(Command("referral"))
async def cmd_referral(message: Message, user: User, session: AsyncSession):
    lang = user.language
    bot_info = await message.bot.get_me()
    text = await _referral_text(user, session, lang, bot_info.username)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("back_main_btn", lang), callback_data="menu_back_main")
    ]])
    await message.answer(text, reply_markup=kb,
                         parse_mode="HTML", disable_web_page_preview=True)
