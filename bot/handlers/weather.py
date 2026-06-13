"""
Weather module.
User types any city/country name in any language.
Uses OpenWeatherMap API.
"""
from __future__ import annotations

import aiohttp

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

from bot.models import User
from bot.locales.i18n import t
from bot.utils.states import WeatherStates
from bot.config import WEATHER_API_KEY

router = Router()


def _weather_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("back_main_btn", lang), callback_data="menu_back_main")
    ]])


async def _fetch_weather(city: str, lang_code: str = "en") -> dict | None:
    """
    Fetch weather from OpenWeatherMap.
    lang_code: 2-letter code passed to OWM for translated descriptions.
    """
    if not WEATHER_API_KEY:
        return None
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": lang_code,
    }
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as r:
                if r.status != 200:
                    return None
                return await r.json()
    except Exception:
        return None


# Map our lang codes to OWM lang codes
_OWM_LANG = {
    "uz": "uz", "ru": "ru", "en": "en",
    "ar": "ar", "tr": "tr", "es": "es", "hi": "hi",
}


# ─────────────────────────────────────────────
# Entry points
# ─────────────────────────────────────────────

@router.callback_query(F.data == "menu_weather")
async def cb_weather_menu(cb: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _weather_keyboard(lang)
    await cb.message.edit_text(t("weather_info", lang), reply_markup=kb)
    await state.set_state(WeatherStates.waiting_city)
    await cb.answer()


@router.message(Command("weather"))
async def cmd_weather(message: Message, user: User, state: FSMContext):
    await state.clear()
    lang = user.language
    kb = _weather_keyboard(lang)
    await message.answer(t("weather_info", lang), reply_markup=kb)
    await state.set_state(WeatherStates.waiting_city)


# ─────────────────────────────────────────────
# City input
# ─────────────────────────────────────────────

@router.message(WeatherStates.waiting_city, F.text)
async def msg_weather_city(
    message: Message,
    state: FSMContext,
    user: User,
):
    lang = user.language
    city_input = message.text.strip()
    owm_lang   = _OWM_LANG.get(lang, "en")

    data = await _fetch_weather(city_input, owm_lang)

    if not data or data.get("cod") != 200:
        await message.answer(t("weather_error", lang))
        return

    city_name   = data["name"]
    temp        = round(data["main"]["temp"])
    humidity    = data["main"]["humidity"]
    wind        = round(data["wind"]["speed"], 1)
    description = data["weather"][0]["description"].capitalize()

    kb = _weather_keyboard(lang)
    await message.answer(
        t("weather_result", lang,
          city=city_name, temp=temp,
          humidity=humidity, wind=wind,
          description=description),
        reply_markup=kb,
        parse_mode="HTML",
    )
    # Stay in waiting_city so user can check another city
