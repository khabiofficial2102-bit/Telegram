"""
Tariff / Subscription module.
Free | Standard | Premium
Payment via balance (deducted) or redirect to top-up.
Referral discounts applied here.
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
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, Subscription
from bot.locales.i18n import t
from bot.utils.states import TariffStates
from bot.services.balance_service import BalanceService
from bot.services.user_service import UserService
from bot.config import (
    STANDARD_MONTHLY, STANDARD_YEARLY,
    PREMIUM_MONTHLY,  PREMIUM_YEARLY,
    REFERRAL_DISCOUNTS,
)
from bot.keyboards.main_keyboard import build_back_btn

router = Router()

_PRICES = {
    ("standard", "monthly"): STANDARD_MONTHLY,
    ("standard", "yearly"):  STANDARD_YEARLY,
    ("premium",  "monthly"): PREMIUM_MONTHLY,
    ("premium",  "yearly"):  PREMIUM_YEARLY,
}

_DURATIONS = {
    "monthly": 30,
    "yearly":  365,
}


def _tariff_main_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_standard", lang), callback_data="tar_choose_standard"),
            InlineKeyboardButton(text=t("btn_premium",  lang), callback_data="tar_choose_premium"),
        ],
        [InlineKeyboardButton(text=t("back_main_btn", lang), callback_data="menu_back_main")],
    ])


def _period_kb(lang: str, tariff: str, std_disc: int, prem_disc: int) -> InlineKeyboardMarkup:
    disc = std_disc if tariff == "standard" else prem_disc

    monthly_price = _PRICES[(tariff, "monthly")]
    yearly_price  = _PRICES[(tariff, "yearly")]

    if disc > 0:
        monthly_price = round(monthly_price * (1 - disc / 100))
        yearly_price  = round(yearly_price  * (1 - disc / 100))

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{t('btn_monthly', lang)} — {monthly_price:,} UZS",
                callback_data=f"tar_period_{tariff}_monthly"
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"{t('btn_yearly', lang)} — {yearly_price:,} UZS",
                callback_data=f"tar_period_{tariff}_yearly"
            ),
        ],
        [InlineKeyboardButton(text=t("back_btn", lang), callback_data="menu_tariff")],
    ])


def _apply_discount(price: int, tariff: str, ref_count: int) -> tuple[int, int]:
    """Return (final_price, discount_pct)."""
    disc = 0
    for (min_refs, t_key), d in sorted(REFERRAL_DISCOUNTS.items(), reverse=True):
        if ref_count >= min_refs and t_key == tariff:
            disc = d
            break
    return round(price * (1 - disc / 100)), disc


# ─────────────────────────────────────────────
# Entry points
# ─────────────────────────────────────────────

@router.callback_query(F.data == "menu_tariff")
async def cb_tariff_menu(cb: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _tariff_main_kb(lang)
    try:
        await cb.message.edit_text(t("tariff_info", lang), reply_markup=kb, parse_mode="HTML")
    except Exception:
        await cb.message.answer(t("tariff_info", lang), reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@router.message(Command("tariff"))
async def cmd_tariff(message: Message, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _tariff_main_kb(lang)
    await message.answer(t("tariff_info", lang), reply_markup=kb, parse_mode="HTML")


# ─────────────────────────────────────────────
# Choose tariff type
# ─────────────────────────────────────────────

@router.callback_query(F.data.in_({"tar_choose_standard", "tar_choose_premium"}))
async def cb_choose_tariff(
    cb: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
):
    lang = user.language
    tariff = "standard" if cb.data == "tar_choose_standard" else "premium"

    # Get referral count for discount preview
    svc = UserService(session)
    ref_count = await svc.get_referral_count(user.id)
    std_disc  = 0
    prem_disc = 0
    for (min_refs, t_key), d in REFERRAL_DISCOUNTS.items():
        if ref_count >= min_refs:
            if t_key == "standard":
                std_disc = max(std_disc, d)
            else:
                prem_disc = max(prem_disc, d)

    kb = _period_kb(lang, tariff, std_disc, prem_disc)
    await state.update_data(tariff=tariff, std_disc=std_disc, prem_disc=prem_disc)
    await state.set_state(TariffStates.choosing_period)
    await cb.message.answer(
        f"{'📦 Standard' if tariff == 'standard' else '💎 Premium'} — {t('btn_monthly', lang)} / {t('btn_yearly', lang)}",
        reply_markup=kb
    )
    await cb.answer()


# ─────────────────────────────────────────────
# Choose period & pay
# ─────────────────────────────────────────────

@router.callback_query(TariffStates.choosing_period, F.data.startswith("tar_period_"))
async def cb_choose_period(
    cb: CallbackQuery,
    state: FSMContext,
    user: User,
    session: AsyncSession,
):
    lang = user.language
    # tar_period_{tariff}_{period}
    _, _, tariff, period = cb.data.split("_", 3)
    data = await state.get_data()

    base_price = _PRICES[(tariff, period)]
    ref_count_svc = UserService(session)
    ref_count = await ref_count_svc.get_referral_count(user.id)
    final_price, disc = _apply_discount(base_price, tariff, ref_count)

    # Check balance
    bal_svc = BalanceService(session)
    balance = await bal_svc.get_amount(user.id)

    if balance < final_price:
        needed = final_price - balance
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=t("balance_topup_btn", lang),
                callback_data="menu_balance"
            )],
            [InlineKeyboardButton(text=t("back_btn", lang), callback_data="menu_tariff")],
        ])
        await cb.message.answer(
            f"❌ Balansingiz yetarli emas.\n"
            f"💰 Kerak: <b>{final_price:,} UZS</b>\n"
            f"💳 Balans: <b>{balance:,.0f} UZS</b>\n"
            f"📉 Yetishmaydi: <b>{needed:,.0f} UZS</b>",
            reply_markup=kb, parse_mode="HTML"
        )
        await cb.answer()
        return

    # Deduct and activate
    await bal_svc.deduct(user.id, final_price, f"tariff_{tariff}_{period}")

    days = _DURATIONS[period]
    expires = datetime.utcnow() + timedelta(days=days)

    user_svc = UserService(session)
    await user_svc.set_tariff(user.id, tariff, expires)

    # Save subscription record
    sub = Subscription(
        user_id=user.id,
        tariff=tariff,
        period=period,
        amount=final_price,
        currency="UZS",
        payment_method="balance",
        status="confirmed",
        discount_applied=disc,
        expires_at=expires,
        confirmed_at=datetime.utcnow(),
    )
    session.add(sub)
    await session.commit()

    # Update pending referral discount (consume used portion)
    u_svc = UserService(session)
    u = await u_svc.get(user.id)
    if u:
        if tariff == "standard":
            u.pending_standard_discount = max(0, u.pending_standard_discount - disc)
        else:
            u.pending_premium_discount = max(0, u.pending_premium_discount - disc)
        await session.commit()

    await cb.message.answer(
        t("tariff_activated", lang,
          tariff=tariff.capitalize(),
          expires=expires.strftime("%d.%m.%Y")),
        parse_mode="HTML"
    )
    await state.clear()
    await cb.answer("✅")
