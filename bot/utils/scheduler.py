"""
APScheduler — all background jobs:
1. Reminders (one-time + daily)    — every minute
2. Daily plans                     — every minute
3. Motivational quotes             — every minute
4. Scheduled ads                   — every minute
5. Tariff expiry check             — every hour
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

logger = logging.getLogger(__name__)
_scheduler: AsyncIOScheduler | None = None


async def start_scheduler(bot: Bot) -> None:
    global _scheduler
    _scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

    _scheduler.add_job(job_reminders,    "interval", minutes=1,  args=[bot],
                       id="reminders",   replace_existing=True)
    _scheduler.add_job(job_daily_plans,  "interval", minutes=1,  args=[bot],
                       id="daily_plans", replace_existing=True)
    _scheduler.add_job(job_quotes,       "interval", minutes=1,  args=[bot],
                       id="quotes",      replace_existing=True)
    _scheduler.add_job(job_ads,          "interval", minutes=1,  args=[bot],
                       id="ads",         replace_existing=True)
    _scheduler.add_job(job_tariff_check, "interval", hours=1,    args=[bot],
                       id="tariff",      replace_existing=True)

    _scheduler.start()
    logger.info("Scheduler started with 5 jobs.")


async def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")


# ─────────────────────────────────────────────
# DB session helper
# ─────────────────────────────────────────────

from bot.models.base import async_session


# ─────────────────────────────────────────────
# 1. REMINDERS
# ─────────────────────────────────────────────

async def job_reminders(bot: Bot) -> None:
    from sqlalchemy import select, update
    from bot.models import Reminder, User
    from bot.locales.i18n import t

    now = datetime.utcnow()
    window_start = now - timedelta(minutes=1)

    async with async_session() as session:
        result = await session.execute(
            select(Reminder).where(
                Reminder.is_active == True,
                Reminder.remind_at >= window_start,
                Reminder.remind_at <= now,
            )
        )
        reminders = result.scalars().all()

        for rem in reminders:
            try:
                u_res = await session.execute(
                    select(User).where(User.id == rem.user_id)
                )
                user = u_res.scalar_one_or_none()
                lang = user.language if user else "uz"

                await bot.send_message(
                    rem.user_id,
                    t("reminder_fired", lang, text=rem.text),
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.warning("Reminder send failed for user %s: %s", rem.user_id, e)

            if rem.is_daily:
                # Reschedule for tomorrow same time
                rem.remind_at = rem.remind_at + timedelta(days=1)
            else:
                rem.is_active = False

        await session.commit()


# ─────────────────────────────────────────────
# 2. DAILY PLANS
# ─────────────────────────────────────────────

async def job_daily_plans(bot: Bot) -> None:
    from sqlalchemy import select
    from bot.models import DailyPlan, User
    from bot.locales.i18n import t

    now = datetime.now()  # local time for HH:MM comparison
    current_hhmm = now.strftime("%H:%M")

    async with async_session() as session:
        result = await session.execute(
            select(DailyPlan).where(
                DailyPlan.is_active == True,
                DailyPlan.send_time == current_hhmm,
            )
        )
        plans = result.scalars().all()

        for plan in plans:
            try:
                u_res = await session.execute(
                    select(User).where(User.id == plan.user_id)
                )
                user = u_res.scalar_one_or_none()
                lang = user.language if user else "uz"

                await bot.send_message(
                    plan.user_id,
                    t("plan_fired", lang, text=plan.text),
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.warning("Daily plan send failed for user %s: %s", plan.user_id, e)


# ─────────────────────────────────────────────
# 3. MOTIVATIONAL QUOTES
# ─────────────────────────────────────────────

async def job_quotes(bot: Bot) -> None:
    from sqlalchemy import select
    from bot.models import MotivationalQuote, User
    from bot.locales.i18n import t
    from bot.services.user_service import UserService

    now = datetime.now()
    current_hhmm = now.strftime("%H:%M")

    async with async_session() as session:
        result = await session.execute(
            select(MotivationalQuote).where(
                MotivationalQuote.is_active == True,
                MotivationalQuote.send_time == current_hhmm,
            )
        )
        quotes = result.scalars().all()

        if not quotes:
            return

        svc = UserService(session)

        for quote in quotes:
            try:
                if quote.language == "all":
                    ids = await svc.all_active_ids()
                else:
                    ids = await svc.all_ids_by_lang(quote.language)

                for uid in ids:
                    try:
                        # Get user lang for translation key
                        u_res = await session.execute(
                            select(User).where(User.id == uid)
                        )
                        u = u_res.scalar_one_or_none()
                        lang = u.language if u else quote.language

                        await bot.send_message(
                            uid,
                            t("morning_quote", lang, quote=quote.text),
                            parse_mode="HTML",
                        )
                    except Exception:
                        pass
            except Exception as e:
                logger.warning("Quote job error: %s", e)


# ─────────────────────────────────────────────
# 4. SCHEDULED ADS
# ─────────────────────────────────────────────

async def job_ads(bot: Bot) -> None:
    from sqlalchemy import select
    from bot.models import ScheduledAd
    from bot.services.user_service import UserService
    from bot.admin.router import _send_ad

    now = datetime.utcnow()

    async with async_session() as session:
        result = await session.execute(
            select(ScheduledAd).where(
                ScheduledAd.is_sent == False,
                ScheduledAd.send_at <= now,
                ScheduledAd.send_at.isnot(None),
            )
        )
        ads = result.scalars().all()

        if not ads:
            return

        svc = UserService(session)

        for ad in ads:
            try:
                if ad.language == "all":
                    ids = await svc.all_active_ids()
                else:
                    ids = await svc.all_ids_by_lang(ad.language)

                for uid in ids:
                    try:
                        await _send_ad(bot, uid, ad.text or "", ad.media_file_id, ad.media_type)
                    except Exception:
                        pass

                ad.is_sent = True
            except Exception as e:
                logger.warning("Ad job error for ad#%s: %s", ad.id, e)

        await session.commit()


# ─────────────────────────────────────────────
# 5. TARIFF EXPIRY CHECK
# ─────────────────────────────────────────────

async def job_tariff_check(bot: Bot) -> None:
    from sqlalchemy import select, update
    from bot.models import User
    from bot.locales.i18n import t

    now = datetime.utcnow()

    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                User.tariff.in_(["standard", "premium"]),
                User.tariff_expires <= now,
            )
        )
        expired_users = result.scalars().all()

        for u in expired_users:
            try:
                await bot.send_message(
                    u.id,
                    f"⚠️ {t('tariff_free', u.language)} — tarifingiz muddati tugadi. "
                    f"Davom ettirish uchun /tariff",
                )
            except Exception:
                pass
            u.tariff = "free"
            u.tariff_expires = None

        if expired_users:
            await session.commit()
            logger.info("Expired %d tariffs.", len(expired_users))
