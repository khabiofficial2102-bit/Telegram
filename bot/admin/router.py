"""
Admin panel — /admin command (only for ADMIN_ID).
14 sections:
 1. Statistika
 2. Hammaga xabar
 3. Reklama (tilga qarab + vaqtli)
 4. Majburiy obuna
 5. Motivatsion iqtibos
 6. Xush kelibsiz xabari
 7. Tugmalar matnini tahrirlash
 8. Ommaviy oferta
 9. Admin tugmasi matni
10. Taqiqlangan so'zlar
11. Foydalanuvchilar ro'yxati
12. Ogohlantirish yuborish
13. Bloklash
14. Blokdan chiqarish
"""
from __future__ import annotations

import asyncio
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import ADMIN_ID, ADMIN_USERNAME, DONATION_LINK
from bot.locales.i18n import t, LANGUAGE_NAMES
from bot.models import (
    User, BannedWord, MandatorySub, MotivationalQuote,
    BotText, ScheduledAd,
)
from bot.services.user_service import UserService
from bot.utils.states import AdminStates

router = Router()

# ── Admin-only filter ────────────────────────────────────────────────────────
def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def _admin_guard(user: User | None) -> bool:
    return user is not None and user.id == ADMIN_ID


# ── Main admin panel keyboard ────────────────────────────────────────────────
def _admin_main_kb() -> InlineKeyboardMarkup:
    sections = [
        ("📊 Statistika",          "adm_stats"),
        ("📢 Hammaga xabar",        "adm_broadcast"),
        ("📣 Reklama",              "adm_ads"),
        ("🔒 Majburiy obuna",       "adm_mandatory"),
        ("💡 Motivatsion iqtibos",  "adm_quotes"),
        ("👋 Xush kelibsiz xabari", "adm_welcome"),
        ("✏️ Tugma matnlari",       "adm_btn_texts"),
        ("📋 Ommaviy oferta",       "adm_offer"),
        ("📞 Admin tugmasi matni",  "adm_admin_text"),
        ("🚫 Taqiqlangan so'zlar",  "adm_banned"),
        ("👥 Foydalanuvchilar",     "adm_users"),
        ("⚠️ Ogohlantirish",        "adm_warn"),
        ("🔴 Bloklash",             "adm_block"),
        ("🟢 Blokdan chiqarish",    "adm_unblock"),
    ]
    rows = []
    for i in range(0, len(sections), 2):
        row = [
            InlineKeyboardButton(text=label, callback_data=cb)
            for label, cb in sections[i:i+2]
        ]
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _back_to_admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm_main")
    ]])


def _lang_kb_admin(prefix: str, include_all: bool = True) -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(LANGUAGE_NAMES), 2):
        items = list(LANGUAGE_NAMES.items())[i:i+2]
        rows.append([
            InlineKeyboardButton(text=name, callback_data=f"{prefix}{code}")
            for code, name in items
        ])
    if include_all:
        rows.append([InlineKeyboardButton(text="🌍 Hammaga", callback_data=f"{prefix}all")])
    rows.append([InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─────────────────────────────────────────────
# /admin command
# ─────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext, user: User | None):
    if not _admin_guard(user):
        return
    await state.clear()
    await message.answer(
        "🛠 <b>Admin Panel</b>\nBo'limni tanlang:",
        reply_markup=_admin_main_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm_main")
async def cb_adm_main(cb: CallbackQuery, state: FSMContext, user: User | None):
    if not _admin_guard(user):
        await cb.answer()
        return
    await state.clear()
    try:
        await cb.message.edit_text(
            "🛠 <b>Admin Panel</b>\nBo'limni tanlang:",
            reply_markup=_admin_main_kb(),
            parse_mode="HTML",
        )
    except Exception:
        await cb.message.answer(
            "🛠 <b>Admin Panel</b>\nBo'limni tanlang:",
            reply_markup=_admin_main_kb(),
            parse_mode="HTML",
        )
    await cb.answer()


# ─────────────────────────────────────────────
# 1. STATISTIKA
# ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_stats")
async def cb_adm_stats(cb: CallbackQuery, user: User | None, session: AsyncSession):
    if not _admin_guard(user):
        await cb.answer()
        return

    svc = UserService(session)
    total   = await svc.total_count()
    active  = await svc.active_count(30)
    blocked = await svc.blocked_count()
    today   = await svc.today_count()
    monthly = await svc.monthly_count()
    langs   = await svc.lang_stats()
    cities  = await svc.city_stats(5)

    lang_lines = "\n".join(
        f"  {LANGUAGE_NAMES.get(k, k)}: <b>{v}</b>"
        for k, v in sorted(langs.items(), key=lambda x: -x[1])
    )
    city_lines = "\n".join(
        f"  {city or '?'}: <b>{cnt}</b>"
        for city, cnt in cities
    ) or "  Ma'lumot yo'q"

    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Jami: <b>{total}</b>\n"
        f"✅ Faol (30 kun): <b>{active}</b>\n"
        f"🚫 Bloklangan: <b>{blocked}</b>\n"
        f"📅 Bugun qo'shilgan: <b>{today}</b>\n"
        f"📆 Oxirgi 30 kun: <b>{monthly}</b>\n\n"
        f"🌐 <b>Tillar bo'yicha:</b>\n{lang_lines}\n\n"
        f"🏙 <b>Top shaharlar:</b>\n{city_lines}"
    )
    await cb.message.edit_text(text, reply_markup=_back_to_admin_kb(), parse_mode="HTML")
    await cb.answer()


# ─────────────────────────────────────────────
# 2. HAMMAGA XABAR (broadcast)
# ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_broadcast")
async def cb_adm_broadcast(cb: CallbackQuery, user: User | None, state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text(
        "📢 <b>Hammaga xabar</b>\n\nRasm, video yoki matn yuboring:",
        reply_markup=_back_to_admin_kb(),
        parse_mode="HTML",
    )
    await state.set_state(AdminStates.broadcast_text)
    await cb.answer()


@router.message(AdminStates.broadcast_text)
async def msg_broadcast(message: Message, state: FSMContext, user: User | None,
                        session: AsyncSession, bot: Bot):
    if not _admin_guard(user):
        return
    svc = UserService(session)
    ids = await svc.all_active_ids()

    sent = 0
    failed = 0
    for uid in ids:
        try:
            if message.photo:
                await bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption)
            elif message.video:
                await bot.send_video(uid, message.video.file_id, caption=message.caption)
            elif message.text:
                await bot.send_message(uid, message.text, parse_mode="HTML")
            sent += 1
            await asyncio.sleep(0.05)  # rate limiting
        except Exception:
            failed += 1

    await message.answer(
        f"✅ Yuborildi: <b>{sent}</b>\n❌ Muvaffaqiyatsiz: <b>{failed}</b>",
        parse_mode="HTML",
        reply_markup=_back_to_admin_kb(),
    )
    await state.clear()


# ─────────────────────────────────────────────
# 3. REKLAMA
# ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_ads")
async def cb_adm_ads(cb: CallbackQuery, user: User | None, state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text(
        "📣 <b>Reklama</b>\nQaysi tilga yuborasiz?",
        reply_markup=_lang_kb_admin("adm_ad_lang_"),
        parse_mode="HTML",
    )
    await state.set_state(AdminStates.ad_choose_lang)
    await cb.answer()


@router.callback_query(AdminStates.ad_choose_lang, F.data.startswith("adm_ad_lang_"))
async def cb_ad_lang(cb: CallbackQuery, state: FSMContext, user: User | None):
    if not _admin_guard(user):
        await cb.answer()
        return
    lang = cb.data.removeprefix("adm_ad_lang_")
    await state.update_data(ad_lang=lang)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏰ Vaqtli yuborish", callback_data="adm_ad_schedule")],
        [InlineKeyboardButton(text="🚀 Hoziroq yuborish", callback_data="adm_ad_now")],
        [InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm_main")],
    ])
    await cb.message.edit_text(
        f"Til: <b>{LANGUAGE_NAMES.get(lang, lang)}</b>\n\nReklama turi:",
        reply_markup=kb, parse_mode="HTML"
    )
    await cb.answer()


@router.callback_query(F.data == "adm_ad_now")
async def cb_ad_now(cb: CallbackQuery, state: FSMContext, user: User | None):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text(
        "📝 Reklama matnini, rasm yoki videoni yuboring:",
        reply_markup=_back_to_admin_kb()
    )
    await state.set_state(AdminStates.ad_input)
    await cb.answer()


@router.callback_query(F.data == "adm_ad_schedule")
async def cb_ad_schedule(cb: CallbackQuery, state: FSMContext, user: User | None):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text(
        "⏰ Yuborish vaqtini kiriting (YYYY-MM-DD HH:MM):",
        reply_markup=_back_to_admin_kb()
    )
    await state.set_state(AdminStates.ad_schedule_time)
    await cb.answer()


@router.message(AdminStates.ad_schedule_time, F.text)
async def msg_ad_schedule_time(message: Message, state: FSMContext, user: User | None):
    if not _admin_guard(user):
        return
    try:
        dt = datetime.strptime(message.text.strip(), "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer("❌ Noto'g'ri format. YYYY-MM-DD HH:MM ko'rinishida yozing.")
        return
    await state.update_data(ad_schedule_dt=dt.isoformat())
    await message.answer("📝 Reklama matnini, rasm yoki videoni yuboring:")
    await state.set_state(AdminStates.ad_input)


@router.message(AdminStates.ad_input)
async def msg_ad_input(
    message: Message,
    state: FSMContext,
    user: User | None,
    session: AsyncSession,
    bot: Bot,
):
    if not _admin_guard(user):
        return
    data = await state.get_data()
    lang = data.get("ad_lang", "all")
    schedule_dt_str = data.get("ad_schedule_dt")
    schedule_dt = datetime.fromisoformat(schedule_dt_str) if schedule_dt_str else None

    media_file_id = None
    media_type = None
    text_content = message.text or message.caption or ""

    if message.photo:
        media_file_id = message.photo[-1].file_id
        media_type = "photo"
    elif message.video:
        media_file_id = message.video.file_id
        media_type = "video"

    ad = ScheduledAd(
        language=lang,
        text=text_content,
        media_file_id=media_file_id,
        media_type=media_type,
        send_at=schedule_dt,
        is_sent=False,
    )
    session.add(ad)
    await session.commit()

    if not schedule_dt:
        # Send immediately
        from bot.services.user_service import UserService as US
        svc = US(session)
        if lang == "all":
            ids = await svc.all_active_ids()
        else:
            ids = await svc.all_ids_by_lang(lang)

        sent = 0
        for uid in ids:
            try:
                await _send_ad(bot, uid, text_content, media_file_id, media_type)
                sent += 1
                await asyncio.sleep(0.05)
            except Exception:
                pass
        ad.is_sent = True
        await session.commit()
        await message.answer(f"✅ Reklama {sent} ta foydalanuvchiga yuborildi.",
                             reply_markup=_back_to_admin_kb())
    else:
        await message.answer(
            f"⏰ Reklama {schedule_dt.strftime('%Y-%m-%d %H:%M')} da yuboriladi.\n"
            f"Til: {LANGUAGE_NAMES.get(lang, lang)}",
            reply_markup=_back_to_admin_kb()
        )
    await state.clear()


async def _send_ad(bot: Bot, uid: int, text: str, file_id: str | None, media_type: str | None):
    if file_id and media_type == "photo":
        await bot.send_photo(uid, file_id, caption=text or None)
    elif file_id and media_type == "video":
        await bot.send_video(uid, file_id, caption=text or None)
    elif text:
        await bot.send_message(uid, text, parse_mode="HTML")


# ─────────────────────────────────────────────
# 4. MAJBURIY OBUNA
# ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_mandatory")
async def cb_adm_mandatory(cb: CallbackQuery, user: User | None, session: AsyncSession,
                           state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return

    result = await session.execute(select(MandatorySub))
    subs = result.scalars().all()

    lines = ["🔒 <b>Majburiy obuna kanallar:</b>\n"]
    for sub in subs:
        lines.append(f"• <code>{sub.chat_id}</code> {sub.chat_title or ''} [{sub.language}]")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="adm_sub_add")],
        [InlineKeyboardButton(text="🗑 Tozalash",        callback_data="adm_sub_clear")],
        [InlineKeyboardButton(text="⬅️ Admin panel",     callback_data="adm_main")],
    ])
    await cb.message.edit_text(
        "\n".join(lines) or "Majburiy obuna yo'q",
        reply_markup=kb, parse_mode="HTML"
    )
    await cb.answer()


@router.callback_query(F.data == "adm_sub_add")
async def cb_sub_add(cb: CallbackQuery, user: User | None, state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text(
        "Qaysi til uchun?",
        reply_markup=_lang_kb_admin("adm_sub_lang_")
    )
    await state.set_state(AdminStates.sub_choose_lang)
    await cb.answer()


@router.callback_query(AdminStates.sub_choose_lang, F.data.startswith("adm_sub_lang_"))
async def cb_sub_lang(cb: CallbackQuery, state: FSMContext, user: User | None):
    if not _admin_guard(user):
        await cb.answer()
        return
    lang = cb.data.removeprefix("adm_sub_lang_")
    await state.update_data(sub_lang=lang)
    await cb.message.edit_text(
        "Kanal ID yoki username kiriting (masalan: @mychannel yoki -1001234567890):\n"
        "Yonida kanal nomini ham yozsa bo'ladi: <code>-100123 Kanal nomi https://t.me/link</code>",
        parse_mode="HTML", reply_markup=_back_to_admin_kb()
    )
    await state.set_state(AdminStates.sub_input)
    await cb.answer()


@router.message(AdminStates.sub_input, F.text)
async def msg_sub_input(message: Message, state: FSMContext, user: User | None,
                        session: AsyncSession, bot: Bot):
    if not _admin_guard(user):
        return
    data = await state.get_data()
    lang = data.get("sub_lang", "all")

    parts = message.text.strip().split(None, 2)
    raw_id = parts[0]
    title  = parts[1] if len(parts) > 1 else None
    link   = parts[2] if len(parts) > 2 else None

    try:
        if raw_id.startswith("@"):
            chat = await bot.get_chat(raw_id)
            chat_id = chat.id
            title = title or chat.title
        else:
            chat_id = int(raw_id)
    except Exception:
        await message.answer("❌ Kanal topilmadi.")
        return

    sub = MandatorySub(
        chat_id=chat_id,
        chat_title=title,
        invite_link=link,
        language=lang,
    )
    session.add(sub)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        await message.answer("❌ Bu kanal allaqachon qo'shilgan.")
        return

    await message.answer(
        f"✅ Kanal qo'shildi: <code>{chat_id}</code> [{LANGUAGE_NAMES.get(lang, lang)}]",
        parse_mode="HTML", reply_markup=_back_to_admin_kb()
    )
    await state.clear()


@router.callback_query(F.data == "adm_sub_clear")
async def cb_sub_clear(cb: CallbackQuery, user: User | None):
    if not _admin_guard(user):
        await cb.answer()
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="adm_sub_clear2"),
        InlineKeyboardButton(text="❌ Bekor",       callback_data="adm_mandatory"),
    ]])
    await cb.message.edit_text("⚠️ Hamma majburiy obunalarni o'chirasizmi?", reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data == "adm_sub_clear2")
async def cb_sub_clear2(cb: CallbackQuery, user: User | None, session: AsyncSession):
    if not _admin_guard(user):
        await cb.answer()
        return
    await session.execute(delete(MandatorySub))
    await session.commit()
    await cb.message.edit_text("🗑 Barcha majburiy obunalar o'chirildi.",
                               reply_markup=_back_to_admin_kb())
    await cb.answer()


# ─────────────────────────────────────────────
# 5. MOTIVATSION IQTIBOS
# ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_quotes")
async def cb_adm_quotes(cb: CallbackQuery, user: User | None, session: AsyncSession):
    if not _admin_guard(user):
        await cb.answer()
        return

    result = await session.execute(select(MotivationalQuote).limit(10))
    quotes = result.scalars().all()
    lines = ["💡 <b>Motivatsion iqtiboslar (oxirgi 10):</b>\n"]
    for q in quotes:
        lang_label = LANGUAGE_NAMES.get(q.language, q.language)
        lines.append(f"[{lang_label} | {q.send_time}] {q.text[:60]}{'...' if len(q.text) > 60 else ''}")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Qo'shish",    callback_data="adm_quote_add")],
        [InlineKeyboardButton(text="🗑 Barchasini o'ch", callback_data="adm_quote_clear")],
        [InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm_main")],
    ])
    await cb.message.edit_text("\n".join(lines), reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "adm_quote_add")
async def cb_quote_add(cb: CallbackQuery, user: User | None, state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text("Qaysi til?", reply_markup=_lang_kb_admin("adm_ql_"))
    await state.set_state(AdminStates.quote_choose_lang)
    await cb.answer()


@router.callback_query(AdminStates.quote_choose_lang, F.data.startswith("adm_ql_"))
async def cb_quote_lang(cb: CallbackQuery, state: FSMContext, user: User | None):
    if not _admin_guard(user):
        await cb.answer()
        return
    lang = cb.data.removeprefix("adm_ql_")
    await state.update_data(q_lang=lang)
    await cb.message.edit_text(
        "⏰ Yuborish vaqtini kiriting (HH:MM):",
        reply_markup=_back_to_admin_kb()
    )
    await state.set_state(AdminStates.quote_time)
    await cb.answer()


@router.message(AdminStates.quote_time, F.text)
async def msg_quote_time(message: Message, state: FSMContext, user: User | None):
    if not _admin_guard(user):
        return
    raw = message.text.strip()
    try:
        datetime.strptime(raw, "%H:%M")
    except ValueError:
        await message.answer("❌ HH:MM formatida yozing (masalan: 07:30)")
        return
    await state.update_data(q_time=raw)
    await message.answer("📝 Iqtibos matnini yozing:")
    await state.set_state(AdminStates.quote_input)


@router.message(AdminStates.quote_input, F.text)
async def msg_quote_input(message: Message, state: FSMContext, user: User | None,
                          session: AsyncSession):
    if not _admin_guard(user):
        return
    data = await state.get_data()
    quote = MotivationalQuote(
        text=message.text.strip(),
        language=data.get("q_lang", "all"),
        send_time=data.get("q_time", "07:00"),
        is_active=True,
    )
    session.add(quote)
    await session.commit()
    await message.answer("✅ Iqtibos qo'shildi!", reply_markup=_back_to_admin_kb())
    await state.clear()


@router.callback_query(F.data == "adm_quote_clear")
async def cb_quote_clear(cb: CallbackQuery, user: User | None):
    if not _admin_guard(user):
        await cb.answer()
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Ha", callback_data="adm_quote_clear2"),
        InlineKeyboardButton(text="❌ Yo'q", callback_data="adm_quotes"),
    ]])
    await cb.message.edit_text("⚠️ Barcha iqtiboslarni o'chirasizmi?", reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data == "adm_quote_clear2")
async def cb_quote_clear2(cb: CallbackQuery, user: User | None, session: AsyncSession):
    if not _admin_guard(user):
        await cb.answer()
        return
    await session.execute(delete(MotivationalQuote))
    await session.commit()
    await cb.message.edit_text("🗑 Barcha iqtiboslar o'chirildi.", reply_markup=_back_to_admin_kb())
    await cb.answer()


# ─────────────────────────────────────────────
# 6. XUSH KELIBSIZ XABARI
# ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_welcome")
async def cb_adm_welcome(cb: CallbackQuery, user: User | None, state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text("Qaysi til uchun tahrirlaysiz?",
                               reply_markup=_lang_kb_admin("adm_wl_", include_all=False))
    await state.set_state(AdminStates.welcome_choose_lang)
    await cb.answer()


@router.callback_query(AdminStates.welcome_choose_lang, F.data.startswith("adm_wl_"))
async def cb_welcome_lang(cb: CallbackQuery, state: FSMContext, user: User | None,
                          session: AsyncSession):
    if not _admin_guard(user):
        await cb.answer()
        return
    lang = cb.data.removeprefix("adm_wl_")
    await state.update_data(edit_lang=lang, edit_key="welcome")

    result = await session.execute(
        select(BotText.text).where(BotText.key == "welcome", BotText.language == lang)
    )
    current = result.scalar_one_or_none() or t("welcome_new", lang)
    await cb.message.edit_text(
        f"Hozirgi matn:\n<code>{current[:200]}</code>\n\nYangi matnni yozing:",
        parse_mode="HTML", reply_markup=_back_to_admin_kb()
    )
    await state.set_state(AdminStates.welcome_input)
    await cb.answer()


@router.message(AdminStates.welcome_input, F.text)
async def msg_welcome_input(message: Message, state: FSMContext, user: User | None,
                            session: AsyncSession):
    if not _admin_guard(user):
        return
    data  = await state.get_data()
    key   = data.get("edit_key", "welcome")
    lang  = data.get("edit_lang", "uz")

    await _upsert_bot_text(session, key, lang, message.text.strip())
    await message.answer("✅ Xush kelibsiz xabari yangilandi!", reply_markup=_back_to_admin_kb())
    await state.clear()


async def _upsert_bot_text(session: AsyncSession, key: str, lang: str, text: str):
    result = await session.execute(
        select(BotText).where(BotText.key == key, BotText.language == lang)
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.text = text
        existing.updated_at = datetime.utcnow()
    else:
        session.add(BotText(key=key, language=lang, text=text))
    await session.commit()


# ─────────────────────────────────────────────
# 7. TUGMALAR MATNI
# ─────────────────────────────────────────────

_EDITABLE_KEYS = [
    ("expenses_info",   "💸 Xarajatlar tushuntirish"),
    ("reminders_info",  "⏰ Eslatmalar tushuntirish"),
    ("currency_info",   "💱 Valyuta tushuntirish"),
    ("plan_info",       "📅 Kunlik reja tushuntirish"),
    ("weather_info",    "🌤 Ob-havo tushuntirish"),
    ("ai_info",         "🤖 AI tushuntirish"),
    ("balance_offer",   "💳 To'lov ofertasi"),
    ("tariff_info",     "⭐ Tarif ma'lumoti"),
    ("referral_info",   "🎁 Referal ma'lumoti"),
    ("help_text",       "ℹ️ Yordam matni"),
]


@router.callback_query(F.data == "adm_btn_texts")
async def cb_adm_btn_texts(cb: CallbackQuery, user: User | None, state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text("Qaysi til?", reply_markup=_lang_kb_admin("adm_btl_", include_all=False))
    await state.set_state(AdminStates.btn_text_lang)
    await cb.answer()


@router.callback_query(AdminStates.btn_text_lang, F.data.startswith("adm_btl_"))
async def cb_btn_text_lang(cb: CallbackQuery, state: FSMContext, user: User | None):
    if not _admin_guard(user):
        await cb.answer()
        return
    lang = cb.data.removeprefix("adm_btl_")
    await state.update_data(edit_lang=lang)

    rows = []
    for i in range(0, len(_EDITABLE_KEYS), 2):
        row = [
            InlineKeyboardButton(text=label, callback_data=f"adm_btk_{key}")
            for key, label in _EDITABLE_KEYS[i:i+2]
        ]
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Admin panel", callback_data="adm_main")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    await cb.message.edit_text("Qaysi tugma matnini tahrirlaysiz?", reply_markup=kb)
    await state.set_state(AdminStates.btn_text_choose)
    await cb.answer()


@router.callback_query(AdminStates.btn_text_choose, F.data.startswith("adm_btk_"))
async def cb_btn_key(cb: CallbackQuery, state: FSMContext, user: User | None,
                     session: AsyncSession):
    if not _admin_guard(user):
        await cb.answer()
        return
    key = cb.data.removeprefix("adm_btk_")
    data = await state.get_data()
    lang = data.get("edit_lang", "uz")

    result = await session.execute(
        select(BotText.text).where(BotText.key == key, BotText.language == lang)
    )
    current = result.scalar_one_or_none() or t(key, lang)
    await state.update_data(edit_key=key)
    await cb.message.edit_text(
        f"Hozirgi:\n<code>{current[:300]}</code>\n\nYangi matni yozing (HTML qo'llab-quvvatlanadi):",
        parse_mode="HTML", reply_markup=_back_to_admin_kb()
    )
    await state.set_state(AdminStates.btn_text_input)
    await cb.answer()


@router.message(AdminStates.btn_text_input, F.text)
async def msg_btn_text_input(message: Message, state: FSMContext, user: User | None,
                             session: AsyncSession):
    if not _admin_guard(user):
        return
    data = await state.get_data()
    await _upsert_bot_text(session, data["edit_key"], data["edit_lang"], message.text.strip())
    await message.answer("✅ Matn yangilandi!", reply_markup=_back_to_admin_kb())
    await state.clear()


# ─────────────────────────────────────────────
# 8. OMMAVIY OFERTA
# ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_offer")
async def cb_adm_offer(cb: CallbackQuery, user: User | None, state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text("Qaysi til uchun ofertani tahrirlaysiz?",
                               reply_markup=_lang_kb_admin("adm_ol_", include_all=False))
    await state.set_state(AdminStates.offer_choose_lang)
    await cb.answer()


@router.callback_query(AdminStates.offer_choose_lang, F.data.startswith("adm_ol_"))
async def cb_offer_lang(cb: CallbackQuery, state: FSMContext, user: User | None,
                        session: AsyncSession):
    if not _admin_guard(user):
        await cb.answer()
        return
    lang = cb.data.removeprefix("adm_ol_")
    await state.update_data(edit_lang=lang, edit_key="offer")
    result = await session.execute(
        select(BotText.text).where(BotText.key == "offer", BotText.language == lang)
    )
    current = result.scalar_one_or_none() or t("offer_text", lang)
    await cb.message.edit_text(
        f"Hozirgi oferta:\n<code>{current[:200]}</code>\n\nYangi ofertani yozing:",
        parse_mode="HTML", reply_markup=_back_to_admin_kb()
    )
    await state.set_state(AdminStates.offer_input)
    await cb.answer()


@router.message(AdminStates.offer_input, F.text)
async def msg_offer_input(message: Message, state: FSMContext, user: User | None,
                          session: AsyncSession):
    if not _admin_guard(user):
        return
    data = await state.get_data()
    await _upsert_bot_text(session, "offer", data.get("edit_lang", "uz"), message.text.strip())
    await message.answer("✅ Oferta yangilandi!", reply_markup=_back_to_admin_kb())
    await state.clear()


# ─────────────────────────────────────────────
# 9. ADMIN TUGMASI MATNI
# ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_admin_text")
async def cb_adm_admin_text(cb: CallbackQuery, user: User | None, state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text("Qaysi til?",
                               reply_markup=_lang_kb_admin("adm_atl_", include_all=False))
    await state.set_state(AdminStates.admin_txt_lang)
    await cb.answer()


@router.callback_query(AdminStates.admin_txt_lang, F.data.startswith("adm_atl_"))
async def cb_admin_text_lang(cb: CallbackQuery, state: FSMContext, user: User | None,
                             session: AsyncSession):
    if not _admin_guard(user):
        await cb.answer()
        return
    lang = cb.data.removeprefix("adm_atl_")
    await state.update_data(edit_lang=lang, edit_key="admin_contact")
    result = await session.execute(
        select(BotText.text).where(BotText.key == "admin_contact", BotText.language == lang)
    )
    current = result.scalar_one_or_none() or t("admin_contact_text", lang,
                                               admin_username=ADMIN_USERNAME,
                                               donation_link=DONATION_LINK)
    await cb.message.edit_text(
        f"Hozirgi:\n<code>{current[:200]}</code>\n\nYangi matnni yozing:",
        parse_mode="HTML", reply_markup=_back_to_admin_kb()
    )
    await state.set_state(AdminStates.admin_txt_input)
    await cb.answer()


@router.message(AdminStates.admin_txt_input, F.text)
async def msg_admin_text_input(message: Message, state: FSMContext, user: User | None,
                               session: AsyncSession):
    if not _admin_guard(user):
        return
    data = await state.get_data()
    await _upsert_bot_text(session, "admin_contact", data.get("edit_lang", "uz"),
                           message.text.strip())
    await message.answer("✅ Admin matni yangilandi!", reply_markup=_back_to_admin_kb())
    await state.clear()


# ─────────────────────────────────────────────
# 10. TAQIQLANGAN SO'ZLAR
# ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_banned")
async def cb_adm_banned(cb: CallbackQuery, user: User | None, session: AsyncSession,
                        state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    result = await session.execute(select(BannedWord))
    words = [row.word for row in result.scalars().all()]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ So'z qo'shish",   callback_data="adm_banned_add")],
        [InlineKeyboardButton(text="❌ So'z o'chirish",   callback_data="adm_banned_del")],
        [InlineKeyboardButton(text="⬅️ Admin panel",      callback_data="adm_main")],
    ])
    word_list = ", ".join(f"<code>{w}</code>" for w in words) or "Yo'q"
    await cb.message.edit_text(
        f"🚫 <b>Taqiqlangan so'zlar:</b>\n{word_list}",
        reply_markup=kb, parse_mode="HTML"
    )
    await cb.answer()


@router.callback_query(F.data == "adm_banned_add")
async def cb_banned_add(cb: CallbackQuery, user: User | None, state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text(
        "Taqiqlangan so'zlarni kiriting (vergul bilan ajrating):",
        reply_markup=_back_to_admin_kb()
    )
    await state.set_state(AdminStates.banned_word_input)
    await cb.answer()


@router.message(AdminStates.banned_word_input, F.text)
async def msg_banned_word(message: Message, state: FSMContext, user: User | None,
                          session: AsyncSession):
    if not _admin_guard(user):
        return
    words = [w.strip().lower() for w in message.text.split(",") if w.strip()]
    added = 0
    for word in words:
        existing = await session.execute(
            select(BannedWord).where(BannedWord.word == word)
        )
        if not existing.scalar_one_or_none():
            session.add(BannedWord(word=word))
            added += 1
    await session.commit()
    await message.answer(f"✅ {added} ta so'z qo'shildi.", reply_markup=_back_to_admin_kb())
    await state.clear()


@router.callback_query(F.data == "adm_banned_del")
async def cb_banned_del(cb: CallbackQuery, user: User | None, state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text(
        "O'chirish uchun so'zlarni kiriting (vergul bilan):",
        reply_markup=_back_to_admin_kb()
    )
    await state.set_state(AdminStates.banned_word_input)
    await cb.answer()


# ─────────────────────────────────────────────
# 11. FOYDALANUVCHILAR RO'YXATI
# ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_users")
async def cb_adm_users(cb: CallbackQuery, user: User | None, session: AsyncSession):
    if not _admin_guard(user):
        await cb.answer()
        return
    svc = UserService(session)
    users = await svc.all_users_info()
    total = len(users)
    lines = [f"👥 <b>Jami: {total}</b>\n"]
    for u in users[:30]:  # show max 30
        uname = f"@{u.username}" if u.username else "—"
        lines.append(f"<code>{u.id}</code> {uname} [{u.language}]")
    if total > 30:
        lines.append(f"\n... va yana {total - 30} ta")

    await cb.message.edit_text(
        "\n".join(lines), reply_markup=_back_to_admin_kb(), parse_mode="HTML"
    )
    await cb.answer()


# ─────────────────────────────────────────────
# 12. OGOHLANTIRISH YUBORISH
# ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_warn")
async def cb_adm_warn(cb: CallbackQuery, user: User | None, state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text(
        "Foydalanuvchi ID yoki @username kiriting:",
        reply_markup=_back_to_admin_kb()
    )
    await state.set_state(AdminStates.warn_user_id)
    await cb.answer()


@router.message(AdminStates.warn_user_id, F.text)
async def msg_warn_user_id(message: Message, state: FSMContext, user: User | None,
                           session: AsyncSession):
    if not _admin_guard(user):
        return
    raw = message.text.strip()
    svc = UserService(session)
    if raw.startswith("@"):
        target = await svc.get_by_username(raw)
    else:
        try:
            target = await svc.get(int(raw))
        except ValueError:
            target = None

    if not target:
        await message.answer("❌ Foydalanuvchi topilmadi.")
        return

    await state.update_data(warn_uid=target.id, warn_lang=target.language)
    await message.answer(f"Ogohlantirish matnini yozing ({LANGUAGE_NAMES.get(target.language, target.language)}):")
    await state.set_state(AdminStates.warn_text)


@router.message(AdminStates.warn_text, F.text)
async def msg_warn_text(message: Message, state: FSMContext, user: User | None,
                        session: AsyncSession, bot: Bot):
    if not _admin_guard(user):
        return
    data = await state.get_data()
    uid  = data["warn_uid"]
    lang = data.get("warn_lang", "uz")
    svc  = UserService(session)
    new_count = await svc.increment_warnings(uid)
    try:
        await bot.send_message(
            uid,
            f"⚠️ {message.text.strip()}\n\n"
            + t("banned_word_warning", lang, count=new_count, max=3),
            parse_mode="HTML"
        )
        await message.answer("✅ Ogohlantirish yuborildi.", reply_markup=_back_to_admin_kb())
    except Exception as e:
        await message.answer(f"❌ Yuborib bo'lmadi: {e}", reply_markup=_back_to_admin_kb())
    await state.clear()


# ─────────────────────────────────────────────
# 13. BLOKLASH
# ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_block")
async def cb_adm_block(cb: CallbackQuery, user: User | None, state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text(
        "Bloklash uchun ID yoki @username kiriting:",
        reply_markup=_back_to_admin_kb()
    )
    await state.set_state(AdminStates.block_user_id)
    await cb.answer()


@router.message(AdminStates.block_user_id, F.text)
async def msg_block_user(message: Message, state: FSMContext, user: User | None,
                         session: AsyncSession, bot: Bot):
    if not _admin_guard(user):
        return
    raw = message.text.strip()
    svc = UserService(session)
    if raw.startswith("@"):
        target = await svc.get_by_username(raw)
    else:
        try:
            target = await svc.get(int(raw))
        except ValueError:
            target = None

    if not target:
        await message.answer("❌ Foydalanuvchi topilmadi.")
        await state.clear()
        return

    await svc.set_blocked(target.id, True)
    lang = target.language

    try:
        await bot.send_message(target.id, t("blocked_msg", lang, admin_username=ADMIN_USERNAME))
    except Exception:
        pass

    await message.answer(
        f"🔴 Foydalanuvchi <code>{target.id}</code> bloklandi.",
        parse_mode="HTML", reply_markup=_back_to_admin_kb()
    )
    await state.clear()


# ─────────────────────────────────────────────
# 14. BLOKDAN CHIQARISH
# ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_unblock")
async def cb_adm_unblock(cb: CallbackQuery, user: User | None, state: FSMContext):
    if not _admin_guard(user):
        await cb.answer()
        return
    await cb.message.edit_text(
        "Blokdan chiqarish uchun ID yoki @username kiriting:",
        reply_markup=_back_to_admin_kb()
    )
    await state.set_state(AdminStates.unblock_user_id)
    await cb.answer()


@router.message(AdminStates.unblock_user_id, F.text)
async def msg_unblock_user(message: Message, state: FSMContext, user: User | None,
                           session: AsyncSession, bot: Bot):
    if not _admin_guard(user):
        return
    raw = message.text.strip()
    svc = UserService(session)
    if raw.startswith("@"):
        target = await svc.get_by_username(raw)
    else:
        try:
            target = await svc.get(int(raw))
        except ValueError:
            target = None

    if not target:
        await message.answer("❌ Foydalanuvchi topilmadi.")
        await state.clear()
        return

    await svc.set_blocked(target.id, False)
    lang = target.language

    try:
        await bot.send_message(target.id, t("unblocked_msg", lang))
    except Exception:
        pass

    await message.answer(
        f"🟢 Foydalanuvchi <code>{target.id}</code> blokdan chiqarildi.",
        parse_mode="HTML", reply_markup=_back_to_admin_kb()
    )
    await state.clear()
