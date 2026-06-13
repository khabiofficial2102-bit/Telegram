"""
Balance & Payment module.
- Show balance
- Top-up flow: offer → choose method (Stars | Card)
- Card: enter amount → show card details → receive receipt → forward to secret channel
- Stars: Telegram invoice
- Admin confirms/rejects from secret channel buttons
"""
from __future__ import annotations

from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, Subscription
from bot.locales.i18n import t
from bot.utils.states import BalanceStates
from bot.services.balance_service import BalanceService
from bot.config import (
    CARD_NUMBER, CARD_HOLDER, SECRET_CHANNEL_ID,
    ADMIN_ID, ADMIN_USERNAME,
)
from bot.keyboards.main_keyboard import build_back_btn, build_confirm_kb

router = Router()

# Stars price per 1000 UZS  (1 Star ≈ ~20 UZS at 2024 rates; tune as needed)
# We'll use a simple approach: Stars amount = round(uzs / 20)
_UZS_PER_STAR = 20


def _balance_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("balance_topup_btn", lang), callback_data="bal_topup")],
        [InlineKeyboardButton(text=t("back_main_btn", lang),     callback_data="menu_back_main")],
    ])


# ─────────────────────────────────────────────
# Entry points
# ─────────────────────────────────────────────

@router.callback_query(F.data == "menu_balance")
async def cb_balance(cb: CallbackQuery, user: User, session: AsyncSession, state: FSMContext):
    await state.clear()
    lang = user.language
    svc = BalanceService(session)
    amount = await svc.get_amount(user.id)
    kb = _balance_keyboard(lang)
    try:
        await cb.message.edit_text(
            t("balance_text", lang, amount=f"{amount:,.0f}"),
            reply_markup=kb, parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            t("balance_text", lang, amount=f"{amount:,.0f}"),
            reply_markup=kb, parse_mode="HTML"
        )
    await cb.answer()


@router.message(Command("balance"))
async def cmd_balance(message: Message, user: User, session: AsyncSession, state: FSMContext):
    await state.clear()
    lang = user.language
    svc = BalanceService(session)
    amount = await svc.get_amount(user.id)
    kb = _balance_keyboard(lang)
    await message.answer(
        t("balance_text", lang, amount=f"{amount:,.0f}"),
        reply_markup=kb, parse_mode="HTML"
    )


# ─────────────────────────────────────────────
# Top-up flow: show offer
# ─────────────────────────────────────────────

@router.callback_query(F.data == "bal_topup")
async def cb_bal_topup(cb: CallbackQuery, user: User, state: FSMContext):
    lang = user.language
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("accept_offer_btn", lang), callback_data="bal_offer_accept")],
        [InlineKeyboardButton(text=t("btn_cancel", lang),       callback_data="menu_balance")],
    ])
    await cb.message.answer(t("balance_offer", lang), reply_markup=kb, parse_mode="HTML")
    await state.set_state(BalanceStates.reading_offer)
    await cb.answer()


@router.callback_query(BalanceStates.reading_offer, F.data == "bal_offer_accept")
async def cb_bal_offer_accept(cb: CallbackQuery, user: User, state: FSMContext):
    lang = user.language
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_pay_stars", lang), callback_data="bal_method_stars")],
        [InlineKeyboardButton(text=t("btn_pay_card",  lang), callback_data="bal_method_card")],
        [InlineKeyboardButton(text=t("btn_cancel",    lang), callback_data="menu_balance")],
    ])
    await cb.message.answer(t("choose_payment", lang), reply_markup=kb)
    await state.set_state(BalanceStates.choosing_method)
    await cb.answer()


# ─────────────────────────────────────────────
# Card payment flow
# ─────────────────────────────────────────────

@router.callback_query(BalanceStates.choosing_method, F.data == "bal_method_card")
async def cb_method_card(cb: CallbackQuery, user: User, state: FSMContext):
    lang = user.language
    await cb.message.answer(t("enter_amount", lang))
    await state.set_state(BalanceStates.entering_amount)
    await cb.answer()


@router.message(BalanceStates.entering_amount, F.text)
async def msg_enter_amount(
    message: Message,
    state: FSMContext,
    user: User,
):
    lang = user.language
    raw = message.text.strip().replace(" ", "").replace(",", "")
    try:
        amount = float(raw)
        if amount < 1000:
            raise ValueError
    except ValueError:
        await message.answer(t("enter_amount", lang))
        return

    await state.update_data(topup_amount=amount, topup_method="card")

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="menu_balance")
    ]])
    await message.answer(
        t("card_payment_info", lang,
          card_number=CARD_NUMBER,
          card_holder=CARD_HOLDER,
          amount=f"{amount:,.0f}"),
        reply_markup=kb,
        parse_mode="HTML",
    )
    await state.set_state(BalanceStates.waiting_receipt)


@router.message(BalanceStates.waiting_receipt, F.photo | F.document)
async def msg_receipt(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
    bot: Bot,
):
    lang = user.language
    data = await state.get_data()
    amount = data.get("topup_amount", 0)

    # Save pending subscription record
    sub = Subscription(
        user_id=user.id,
        tariff="balance_topup",
        period="once",
        amount=amount,
        currency="UZS",
        payment_method="card",
        status="pending",
    )
    session.add(sub)
    await session.commit()
    sub_id = sub.id

    # Forward receipt to secret channel with confirm/reject buttons
    caption = (
        f"💳 <b>To'lov cheki</b>\n\n"
        f"👤 User: <a href='tg://user?id={user.id}'>{user.first_name or user.full_name or user.id}</a>\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"💰 Summa: <b>{amount:,.0f} UZS</b>\n"
        f"📋 Sub ID: <code>{sub_id}</code>"
    )
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tasdiqlash",  callback_data=f"pay_confirm_{sub_id}"),
        InlineKeyboardButton(text="❌ Rad etish",   callback_data=f"pay_reject_{sub_id}"),
    ]])

    try:
        if message.photo:
            file_id = message.photo[-1].file_id
            await bot.send_photo(
                SECRET_CHANNEL_ID, photo=file_id,
                caption=caption, reply_markup=admin_kb, parse_mode="HTML"
            )
            # Also send to admin directly if secret channel not set
            if not SECRET_CHANNEL_ID:
                await bot.send_photo(
                    ADMIN_ID, photo=file_id,
                    caption=caption, reply_markup=admin_kb, parse_mode="HTML"
                )
        elif message.document:
            file_id = message.document.file_id
            await bot.send_document(
                SECRET_CHANNEL_ID, document=file_id,
                caption=caption, reply_markup=admin_kb, parse_mode="HTML"
            )
            if not SECRET_CHANNEL_ID:
                await bot.send_document(
                    ADMIN_ID, document=file_id,
                    caption=caption, reply_markup=admin_kb, parse_mode="HTML"
                )
    except Exception:
        # Fallback: send text to admin
        await bot.send_message(ADMIN_ID, caption, reply_markup=admin_kb, parse_mode="HTML")

    await message.answer(t("receipt_received", lang))
    await state.clear()


# ─────────────────────────────────────────────
# Telegram Stars payment
# ─────────────────────────────────────────────

@router.callback_query(BalanceStates.choosing_method, F.data == "bal_method_stars")
async def cb_method_stars(cb: CallbackQuery, user: User, state: FSMContext):
    lang = user.language
    await cb.message.answer(t("enter_amount", lang))
    await state.set_state(BalanceStates.waiting_stars)
    await cb.answer()


@router.message(BalanceStates.waiting_stars, F.text)
async def msg_stars_amount(
    message: Message,
    state: FSMContext,
    user: User,
    bot: Bot,
):
    lang = user.language
    raw = message.text.strip().replace(" ", "").replace(",", "")
    try:
        amount_uzs = float(raw)
        if amount_uzs < 1000:
            raise ValueError
    except ValueError:
        await message.answer(t("enter_amount", lang))
        return

    stars_amount = max(1, round(amount_uzs / _UZS_PER_STAR))

    await state.update_data(topup_amount=amount_uzs, stars_amount=stars_amount)

    # Send Telegram Stars invoice
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="💰 Balance Top-up",
        description=f"Add {amount_uzs:,.0f} UZS to your balance",
        payload=f"balance_{user.id}_{amount_uzs}",
        currency="XTR",  # Telegram Stars
        prices=[LabeledPrice(label="Balance", amount=stars_amount)],
    )
    await state.set_state(BalanceStates.waiting_receipt)


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(
    message: Message,
    user: User,
    session: AsyncSession,
    state: FSMContext,
):
    lang = user.language
    payload = message.successful_payment.invoice_payload

    # Parse amount from payload: "balance_{user_id}_{amount}"
    try:
        parts = payload.split("_")
        amount_uzs = float(parts[-1])
    except Exception:
        amount_uzs = 0

    if amount_uzs > 0:
        svc = BalanceService(session)
        await svc.add(user.id, amount_uzs, "topup_stars", f"Telegram Stars payment")
        await message.answer(
            t("balance_added", lang, amount=f"{amount_uzs:,.0f}"),
            parse_mode="HTML"
        )

    await state.clear()


# ─────────────────────────────────────────────
# Admin confirm / reject (from secret channel)
# ─────────────────────────────────────────────

@router.callback_query(F.data.startswith("pay_confirm_"))
async def cb_pay_confirm(
    cb: CallbackQuery,
    session: AsyncSession,
    bot: Bot,
):
    sub_id = int(cb.data.removeprefix("pay_confirm_"))

    # Double-confirm
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Ha, tasdiqlash",  callback_data=f"pay_confirm2_{sub_id}"),
        InlineKeyboardButton(text="❌ Bekor qilish",    callback_data=f"pay_cancel_{sub_id}"),
    ]])
    await cb.message.edit_reply_markup(reply_markup=kb)
    await cb.answer("Tasdiqlash uchun yana bir marta bosing")


@router.callback_query(F.data.startswith("pay_confirm2_"))
async def cb_pay_confirm2(
    cb: CallbackQuery,
    session: AsyncSession,
    bot: Bot,
):
    sub_id = int(cb.data.removeprefix("pay_confirm2_"))

    result = await session.execute(select(Subscription).where(Subscription.id == sub_id))
    sub = result.scalar_one_or_none()

    if not sub or sub.status != "pending":
        await cb.answer("Already processed", show_alert=True)
        return

    sub.status = "confirmed"
    sub.confirmed_at = datetime.utcnow()
    await session.commit()

    # Add to balance
    svc = BalanceService(session)
    new_bal = await svc.add(sub.user_id, sub.amount, "topup_card", f"Sub#{sub_id}")

    # Notify user
    try:
        user_result = await session.execute(
            __import__("sqlalchemy", fromlist=["select"]).select(
                __import__("bot.models", fromlist=["User"]).User
            ).where(
                __import__("bot.models", fromlist=["User"]).User.id == sub.user_id
            )
        )
        u = user_result.scalar_one_or_none()
        lang = u.language if u else "uz"
        await bot.send_message(
            sub.user_id,
            t("balance_added", lang, amount=f"{sub.amount:,.0f}"),
            parse_mode="HTML"
        )
    except Exception:
        pass

    await cb.message.edit_caption(
        caption=(cb.message.caption or "") + f"\n\n✅ <b>Tasdiqlandi!</b> Balans: +{sub.amount:,.0f} UZS",
        parse_mode="HTML"
    )
    await cb.answer("✅ Tasdiqlandi!")


@router.callback_query(F.data.startswith("pay_reject_"))
async def cb_pay_reject(
    cb: CallbackQuery,
    session: AsyncSession,
    bot: Bot,
):
    sub_id = int(cb.data.removeprefix("pay_reject_"))

    # Double-confirm rejection
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="❌ Ha, rad etish",   callback_data=f"pay_reject2_{sub_id}"),
        InlineKeyboardButton(text="⬅️ Bekor qilish",   callback_data=f"pay_cancel_{sub_id}"),
    ]])
    await cb.message.edit_reply_markup(reply_markup=kb)
    await cb.answer("Rad etish uchun yana bir marta bosing")


@router.callback_query(F.data.startswith("pay_reject2_"))
async def cb_pay_reject2(
    cb: CallbackQuery,
    session: AsyncSession,
    bot: Bot,
):
    sub_id = int(cb.data.removeprefix("pay_reject2_"))

    result = await session.execute(select(Subscription).where(Subscription.id == sub_id))
    sub = result.scalar_one_or_none()

    if not sub:
        await cb.answer("Not found", show_alert=True)
        return

    sub.status = "rejected"
    await session.commit()

    try:
        from bot.models import User as UserModel
        from sqlalchemy import select as sa_select
        u_res = await session.execute(sa_select(UserModel).where(UserModel.id == sub.user_id))
        u = u_res.scalar_one_or_none()
        lang = u.language if u else "uz"
        await bot.send_message(sub.user_id, t("payment_rejected", lang), parse_mode="HTML")
    except Exception:
        pass

    await cb.message.edit_caption(
        caption=(cb.message.caption or "") + "\n\n❌ <b>Rad etildi</b>",
        parse_mode="HTML"
    )
    await cb.answer("❌ Rad etildi")


@router.callback_query(F.data.startswith("pay_cancel_"))
async def cb_pay_cancel(cb: CallbackQuery):
    """Restore original confirm/reject buttons."""
    sub_id = cb.data.split("_")[-1]
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pay_confirm_{sub_id}"),
        InlineKeyboardButton(text="❌ Rad etish",  callback_data=f"pay_reject_{sub_id}"),
    ]])
    await cb.message.edit_reply_markup(reply_markup=kb)
    await cb.answer()
