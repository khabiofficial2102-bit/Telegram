"""
AI Assistant module.
20+ sub-functions, balance-based access.
Free tier: 1 use; then 3000 UZS per use OR subscription.
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
from bot.locales.i18n import t
from bot.utils.states import AIStates
from bot.services.balance_service import BalanceService
from bot.services.user_service import UserService
from bot.services.ai_service import call_openai
from bot.config import AI_FUNCTION_PRICE
from bot.keyboards.main_keyboard import build_back_btn

router = Router()

# ── Sub-function definitions ─────────────────────────────────────────────────
AI_FUNCTIONS: list[tuple[str, str]] = [
    ("ai_chat",        "💬 Suhbat / Chat"),
    ("ai_presentation","🆕 Taqdimot (Slayd) Yaratish"),
    ("ai_referat",     "📚 Refarat Yaratish"),
    ("ai_mustaqil",    "📑 Mustaqil Ish Yaratish"),
    ("ai_kurs",        "📘 Kurs ishi yaratish"),
    ("ai_image",       "🖼 Rasm Yaratish (Ai)"),
    ("ai_essay",       "📝 Insho/Essey yaratish"),
    ("ai_crossword",   "🧩 Krosvord yaratish"),
    ("ai_flashcard",   "🃏 Flesh kartalar yaratish"),
    ("ai_quiz",        "📝 Quiz/Test yaratish"),
    ("ai_lesson",      "🗓 Dars Reja"),
    ("ai_resume",      "🧾 Rezyume yaratish"),
    ("ai_article",     "✅ Maqola yaratish"),
    ("ai_thesis",      "🎓 Tezis yaratish"),
    ("ai_infographic", "📊 Infografika yaratish"),
    ("ai_url_pres",    "📄 Fayl yoki URL bo'yicha taqdimot"),
    ("ai_slide_pro",   "🚀 Slayd Pro"),
    ("ai_img_pdf",     "📄 Rasmni PDF ga aylantirish"),
    ("ai_convert",     "🔄 Fayl formatini o'zgartirish"),
    ("ai_archive",     "📦 Arxiv/zip yaratish"),
    ("ai_sort_game",   "🧺 Saralash o'yini"),
]

# System prompts per function key
_SYSTEM_PROMPTS: dict[str, str] = {
    "ai_chat":         "You are a helpful, friendly assistant. Answer concisely.",
    "ai_presentation": "Create a well-structured presentation/slideshow outline with titles and bullet points for the given topic.",
    "ai_referat":      "Write a detailed academic essay/report on the given topic with introduction, main body, and conclusion.",
    "ai_mustaqil":     "Write an independent study assignment on the given topic with research questions and findings.",
    "ai_kurs":         "Write a course work (kurs ishi) outline and content on the given topic.",
    "ai_essay":        "Write a well-structured essay on the given topic.",
    "ai_crossword":    "Create a crossword puzzle with clues and answers on the given topic. Format: WORD: clue",
    "ai_flashcard":    "Create 10 flashcards (question + answer pairs) on the given topic.",
    "ai_quiz":         "Create a 10-question multiple-choice quiz on the given topic with answer key.",
    "ai_lesson":       "Create a detailed lesson plan for teaching the given topic.",
    "ai_resume":       "Create a professional resume/CV based on the provided information.",
    "ai_article":      "Write a well-researched, engaging article on the given topic.",
    "ai_thesis":       "Write a thesis statement and outline for the given topic.",
    "ai_infographic":  "Create textual content for an infographic on the given topic with sections and key points.",
    "ai_url_pres":     "Based on the provided URL or file description, create a presentation outline.",
    "ai_slide_pro":    "Create a professional slide deck with images, charts, and tables suggestions for the given topic.",
    "ai_img_pdf":      "Describe how to convert the provided image to PDF, and provide OCR text if image text is given.",
    "ai_convert":      "Help convert the described file from one format to another, providing instructions.",
    "ai_archive":      "Provide instructions and file structure for creating an archive/zip with the given contents.",
    "ai_sort_game":    "Create a sorting/categorization game with items and categories on the given topic.",
    "ai_image":        "Describe a detailed image generation prompt for the given subject (DALL-E style).",
}


def _ai_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(AI_FUNCTIONS), 2):
        row = []
        for key, label in AI_FUNCTIONS[i:i+2]:
            row.append(InlineKeyboardButton(text=label, callback_data=f"ai_fn_{key}"))
        rows.append(row)
    rows.append([InlineKeyboardButton(text=t("back_main_btn", lang), callback_data="menu_back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _back_to_ai_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("back_btn", lang), callback_data="menu_ai"),
    ]])


async def _check_access(user: User, session: AsyncSession) -> bool:
    """Return True if user can use AI (has subscription, or has balance, or free slot)."""
    from datetime import datetime
    # Premium/Standard with valid subscription → free access
    if user.tariff in ("standard", "premium"):
        if user.tariff_expires is None or user.tariff_expires > datetime.utcnow():
            return True
    # Free tier: 1 use
    if user.ai_free_used < 1:
        return True
    # Has enough balance
    svc = BalanceService(session)
    return await svc.has_enough(user.id, AI_FUNCTION_PRICE)


async def _deduct_or_mark(user: User, session: AsyncSession) -> bool:
    """Deduct balance or mark free use. Returns False if can't pay."""
    from datetime import datetime
    if user.tariff in ("standard", "premium"):
        if user.tariff_expires is None or user.tariff_expires > datetime.utcnow():
            return True  # subscription covers it

    if user.ai_free_used < 1:
        svc = UserService(session)
        await svc.increment_ai_free(user.id)
        return True

    svc = BalanceService(session)
    result = await svc.deduct(user.id, AI_FUNCTION_PRICE, "ai_use")
    return result is not None


# ─────────────────────────────────────────────
# Entry points
# ─────────────────────────────────────────────

@router.callback_query(F.data == "menu_ai")
async def cb_ai_menu(cb: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _ai_menu_keyboard(lang)
    try:
        await cb.message.edit_text(t("ai_info", lang), reply_markup=kb, parse_mode="HTML")
    except Exception:
        await cb.message.answer(t("ai_info", lang), reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@router.message(Command("ai"))
async def cmd_ai(message: Message, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _ai_menu_keyboard(lang)
    await message.answer(t("ai_info", lang), reply_markup=kb, parse_mode="HTML")


# ─────────────────────────────────────────────
# Function selected
# ─────────────────────────────────────────────

@router.callback_query(F.data.startswith("ai_fn_"))
async def cb_ai_function(
    cb: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
):
    lang = user.language
    fn_key = cb.data.removeprefix("ai_fn_")

    # Access check
    if not await _check_access(user, session):
        await cb.answer(t("ai_no_balance", lang), show_alert=True)
        return

    await state.update_data(ai_fn=fn_key)
    await state.set_state(AIStates.waiting_prompt)

    await cb.message.answer(t("ai_ask_prompt", lang))
    await cb.answer()


# ─────────────────────────────────────────────
# Receive prompt & call OpenAI
# ─────────────────────────────────────────────

@router.message(AIStates.waiting_prompt, F.text)
async def msg_ai_prompt(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    lang = user.language
    data = await state.get_data()
    fn_key = data.get("ai_fn", "ai_chat")

    # Final access + deduct
    if not await _deduct_or_mark(user, session):
        await message.answer(t("ai_no_balance", lang))
        await state.clear()
        return

    processing_msg = await message.answer(t("ai_processing", lang))

    system_prompt = _SYSTEM_PROMPTS.get(fn_key, _SYSTEM_PROMPTS["ai_chat"])
    user_prompt   = message.text.strip()

    result = await call_openai(system_prompt, user_prompt)

    try:
        await processing_msg.delete()
    except Exception:
        pass

    if not result:
        await message.answer(t("ai_error", lang))
        await state.clear()
        return

    # Deduction notice (only for balance users)
    from datetime import datetime
    is_sub = user.tariff in ("standard", "premium") and (
        user.tariff_expires is None or user.tariff_expires > datetime.utcnow()
    )
    if not is_sub and user.ai_free_used >= 1:
        await message.answer(t("ai_deducted", lang, amount=AI_FUNCTION_PRICE))

    kb = _back_to_ai_kb(lang)

    # Split long responses
    MAX_LEN = 4000
    if len(result) <= MAX_LEN:
        await message.answer(result, reply_markup=kb, parse_mode="HTML")
    else:
        chunks = [result[i:i+MAX_LEN] for i in range(0, len(result), MAX_LEN)]
        for i, chunk in enumerate(chunks):
            if i == len(chunks) - 1:
                await message.answer(chunk, reply_markup=kb)
            else:
                await message.answer(chunk)

    # Stay in waiting_prompt for follow-up
    await state.set_state(AIStates.waiting_prompt)


# ─────────────────────────────────────────────
# Chat mode (continuous conversation)
# ─────────────────────────────────────────────

@router.message(AIStates.chatting, F.text)
async def msg_ai_chat(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    lang = user.language

    if not await _deduct_or_mark(user, session):
        await message.answer(t("ai_no_balance", lang))
        await state.set_state(AIStates.waiting_prompt)
        return

    processing_msg = await message.answer(t("ai_processing", lang))
    result = await call_openai(_SYSTEM_PROMPTS["ai_chat"], message.text.strip())

    try:
        await processing_msg.delete()
    except Exception:
        pass

    if not result:
        await message.answer(t("ai_error", lang))
        return

    kb = _back_to_ai_kb(lang)
    await message.answer(result, reply_markup=kb)
