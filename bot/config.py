import os
from dotenv import load_dotenv

load_dotenv()

# ===== BOT =====
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")

# ===== SECRET CHANNEL =====
SECRET_CHANNEL_ID: int = int(os.getenv("SECRET_CHANNEL_ID", "0"))

# ===== CARD PAYMENT =====
CARD_NUMBER: str = os.getenv("CARD_NUMBER", "0000 0000 0000 0000")
CARD_HOLDER: str = os.getenv("CARD_HOLDER", "CARD HOLDER")

# ===== APIS =====
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
CURRENCY_API_KEY: str = os.getenv("CURRENCY_API_KEY", "")

# ===== DATABASE =====
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot/data/database.db")

# ===== OTHER =====
DONATION_LINK: str = os.getenv("DONATION_LINK", "https://t.me/donate")
TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Tashkent")

# ===== TARIFF PRICES (UZS) =====
STANDARD_MONTHLY: int = 49_900
STANDARD_YEARLY: int = 499_900
PREMIUM_MONTHLY: int = 99_900
PREMIUM_YEARLY: int = 999_900
AI_FUNCTION_PRICE: int = 3_000   # per use for free-tier users

# ===== REFERRAL DISCOUNTS =====
# Keys: (referral_count, tariff) -> discount_percent
REFERRAL_DISCOUNTS = {
    (5,  "standard"): 20,
    (5,  "premium"):   5,
    (10, "standard"): 37,
    (10, "premium"):  10,
}

# ===== SUPPORTED LANGUAGES =====
LANGUAGES = ["uz", "en", "ru", "ar", "tr", "es", "hi"]

LANGUAGE_FLAGS = {
    "uz": "🇺🇿 O'zbek",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
    "ar": "🇸🇦 العربية",
    "tr": "🇹🇷 Türkçe",
    "es": "🇪🇸 Español",
    "hi": "🇮🇳 हिन्दी",
}

# ===== BANNED WORDS MAX WARNINGS =====
MAX_WARNINGS: int = 3
