"""
Central i18n module.

Usage:
    from bot.locales import t
    text = t("welcome_new", lang="uz")
    text = t("expense_added", lang="en", amount=50, currency="USD", desc="food")
"""
from .uz import UZ
from .en import EN
from .ru import RU
from .ar import AR
from .tr import TR
from .es import ES
from .hi import HI

TEXTS: dict[str, dict] = {
    "uz": UZ,
    "en": EN,
    "ru": RU,
    "ar": AR,
    "tr": TR,
    "es": ES,
    "hi": HI,
}

# Telegram language_code -> our lang key mapping
TG_LANG_MAP: dict[str, str] = {
    "uz": "uz",
    "ru": "ru",
    "en": "en",
    "ar": "ar",
    "tr": "tr",
    "es": "es",
    "hi": "hi",
    # additional variants
    "be": "ru",   # Belarusian -> Russian
    "uk": "ru",   # Ukrainian -> Russian
    "kk": "ru",   # Kazakh -> Russian (fallback)
    "ky": "uz",   # Kyrgyz -> Uzbek (closest)
    "tg": "uz",   # Tajik -> Uzbek (closest)
    "fa": "ar",   # Persian -> Arabic (closest)
    "pt": "es",   # Portuguese -> Spanish (closest)
}

LANGUAGE_NAMES: dict[str, str] = {
    "uz": "🇺🇿 O'zbek",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
    "ar": "🇸🇦 العربية",
    "tr": "🇹🇷 Türkçe",
    "es": "🇪🇸 Español",
    "hi": "🇮🇳 हिन्दी",
}


def detect_lang(tg_language_code: str | None) -> str:
    """Map Telegram's language_code to our supported language. Default: 'uz'."""
    if not tg_language_code:
        return "uz"
    code = tg_language_code.lower().split("-")[0]   # e.g. "en-US" -> "en"
    return TG_LANG_MAP.get(code, "uz")


def t(key: str, lang: str = "uz", **kwargs) -> str:
    """
    Get translated text by key and language.
    Falls back to English, then Uzbek if key not found.
    Supports .format(**kwargs) placeholders.
    """
    lang = lang if lang in TEXTS else "uz"
    text = TEXTS[lang].get(key) or TEXTS["en"].get(key) or TEXTS["uz"].get(key, f"[{key}]")
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def get_lang_name(lang: str) -> str:
    return LANGUAGE_NAMES.get(lang, lang)
