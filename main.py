"""
@Startdaily_bot — Entry point.
Run: python main.py
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN, ADMIN_ID
from bot.models import init_db
from bot.middlewares import (
    DbSessionMiddleware,
    UserMiddleware,
    BlockMiddleware,
    BannedWordMiddleware,
    SubscriptionMiddleware,
)
from bot.handlers import get_all_routers
from bot.keyboards.main_keyboard import BOT_COMMANDS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    logger.info("Initialising database...")
    await init_db()

    logger.info("Setting bot commands...")
    await bot.set_my_commands(BOT_COMMANDS)

    logger.info("Starting scheduler...")
    from bot.utils.scheduler import start_scheduler
    await start_scheduler(bot)

    logger.info("Bot started. Admin ID: %s", ADMIN_ID)
    try:
        await bot.send_message(ADMIN_ID, "✅ Bot ishga tushdi / Bot started!")
    except Exception:
        pass


async def on_shutdown(bot: Bot) -> None:
    logger.info("Bot shutting down...")
    from bot.utils.scheduler import stop_scheduler
    await stop_scheduler()


async def main() -> None:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set in .env!")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # ---- Middleware stack (order matters) ----
    # 1. DB session must be first
    dp.update.middleware(DbSessionMiddleware())
    # 2. Load user
    dp.update.middleware(UserMiddleware())
    # 3. Block check
    dp.update.middleware(BlockMiddleware())
    # 4. Banned word check (messages only, but registered on update)
    dp.update.middleware(BannedWordMiddleware())
    # 5. Subscription check
    dp.update.middleware(SubscriptionMiddleware())

    # ---- Register all routers ----
    for router in get_all_routers():
        dp.include_router(router)

    # ---- Lifecycle hooks ----
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Starting polling...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
