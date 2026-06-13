"""Register all routers."""
from aiogram import Router

from .start import router as start_router
from .menu import router as menu_router
from .expenses import router as expenses_router
from .reminders import router as reminders_router
from .currency import router as currency_router
from .daily_plan import router as daily_plan_router
from .weather import router as weather_router
from .profile import router as profile_router
from .ai import router as ai_router
from .balance import router as balance_router
from .tariff import router as tariff_router
from .referral import router as referral_router
from .settings import router as settings_router
from .admin_contact import router as admin_contact_router
from ..admin.router import router as admin_router


def get_all_routers() -> list[Router]:
    return [
        start_router,
        menu_router,
        expenses_router,
        reminders_router,
        currency_router,
        daily_plan_router,
        weather_router,
        profile_router,
        ai_router,
        balance_router,
        tariff_router,
        referral_router,
        settings_router,
        admin_contact_router,
        admin_router,
    ]
