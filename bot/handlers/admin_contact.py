"""Admin contact button handler."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.models import User, BotText
from bot.locales.i18n import t
from bot.config import ADMIN_USERNAME, DONATION_LINK
from bot.keyboards.main_keyboard import build_back_btn

router = Router()


async def _get_admin_text(session: AsyncSession, lang: str) -> str:
    result = await session.execute(
        select(BotText.text).where(BotText.key == "admin_contact", BotText.language == lang)
    )
    custom = result.scalar_one_or_none()
    if custom:
        return custom
    return t("admin_contact_text", lang,
             admin_username=ADMIN_USERNAME,
             donation_link=DONATION_LINK)


@router.callback_query(F.data == "menu_admin_contact")
async def cb_admin_contact(cb: CallbackQuery, user: User, session: AsyncSession):
    lang = user.language
    text = await _get_admin_text(session, lang)
    kb = build_back_btn(lang)
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML",
                                disable_web_page_preview=True)
    await cb.answer()


@router.message(Command("admin_contact"))
async def cmd_admin_contact(message: Message, user: User, session: AsyncSession):
    lang = user.language
    text = await _get_admin_text(session, lang)
    kb = build_back_btn(lang)
    await message.answer(text, reply_markup=kb, parse_mode="HTML",
                         disable_web_page_preview=True)
