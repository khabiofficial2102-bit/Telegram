"""
Currency resolution + conversion.
resolve_currency("dollar") → "USD"
resolve_currency("O'zbekiston") → "UZS"
convert_amount(100, "USD", "UZS") → float
"""
from __future__ import annotations

import aiohttp
from bot.config import CURRENCY_API_KEY

# ── Alias map: lowercased word → ISO 4217 code ────────────────────────────
_ALIASES: dict[str, str] = {
    # UZS
    "uzs": "UZS", "so'm": "UZS", "som": "UZS", "sum": "UZS",
    "o'zbekiston": "UZS", "uzbekistan": "UZS", "uzbek": "UZS", "узс": "UZS",
    "сум": "UZS", "ўзбекистон": "UZS",
    # USD
    "usd": "USD", "dollar": "USD", "dollars": "USD", "доллар": "USD",
    "дол": "USD", "долларов": "USD", "us": "USD", "usa": "USD",
    "america": "USD", "american": "USD", "dollar$": "USD",
    # EUR
    "eur": "EUR", "euro": "EUR", "euros": "EUR", "евро": "EUR",
    "europe": "EUR", "european": "EUR",
    # RUB
    "rub": "RUB", "ruble": "RUB", "rubles": "RUB", "рубль": "RUB",
    "рублей": "RUB", "russia": "RUB", "russian": "RUB", "россия": "RUB",
    "rossiya": "RUB", "rus": "RUB",
    # TRY
    "try": "TRY", "lira": "TRY", "turk": "TRY", "turkey": "TRY",
    "türkiye": "TRY", "türk": "TRY", "туркия": "TRY",
    # GBP
    "gbp": "GBP", "pound": "GBP", "pounds": "GBP", "sterling": "GBP",
    "britain": "GBP", "uk": "GBP", "england": "GBP",
    # JPY
    "jpy": "JPY", "yen": "JPY", "japan": "JPY", "японский": "JPY",
    # CNY
    "cny": "CNY", "yuan": "CNY", "china": "CNY", "chinese": "CNY",
    # SAR
    "sar": "SAR", "riyal": "SAR", "rial": "SAR",
    "saudi": "SAR", "arabia": "SAR",
    # INR
    "inr": "INR", "rupee": "INR", "rupees": "INR", "india": "INR",
    "indian": "INR", "hindiston": "INR",
    # KZT
    "kzt": "KZT", "tenge": "KZT", "kazakhstan": "KZT", "казахстан": "KZT",
    # AED
    "aed": "AED", "dirham": "AED", "uae": "AED", "dubai": "AED",
    # KRW
    "krw": "KRW", "won": "KRW", "korea": "KRW", "korean": "KRW",
    # CAD
    "cad": "CAD", "canadian": "CAD", "canada": "CAD",
    # AUD
    "aud": "AUD", "australian": "AUD", "australia": "AUD",
    # CHF
    "chf": "CHF", "franc": "CHF", "swiss": "CHF", "switzerland": "CHF",
    # PLN
    "pln": "PLN", "zloty": "PLN", "poland": "PLN",
    # BRL
    "brl": "BRL", "real": "BRL", "brazil": "BRL",
    # MXN
    "mxn": "MXN", "peso": "MXN", "mexico": "MXN",
    # EGP
    "egp": "EGP", "egypt": "EGP", "egyptian": "EGP", "misir": "EGP",
    # PKR
    "pkr": "PKR", "pakistan": "PKR",
    # UAH
    "uah": "UAH", "hryvnia": "UAH", "ukraine": "UAH",
    # BYR / BYN
    "byn": "BYN", "belarus": "BYN",
    # AZN
    "azn": "AZN", "manat": "AZN", "azerbaijan": "AZN",
    # GEL
    "gel": "GEL", "lari": "GEL", "georgia": "GEL",
    # KGS
    "kgs": "KGS", "kyrgyzstan": "KGS", "som_kz": "KGS",
    # TJS
    "tjs": "TJS", "somoni": "TJS", "tajikistan": "TJS",
    # TMT
    "tmt": "TMT", "manat_tm": "TMT", "turkmenistan": "TMT",
}

# Build uppercase lookup too
_LOOKUP: dict[str, str] = {}
for k, v in _ALIASES.items():
    _LOOKUP[k.lower()] = v
    _LOOKUP[v.lower()] = v  # ISO code maps to itself


def resolve_currency(raw: str) -> str | None:
    """Convert user input to ISO currency code. Case-insensitive."""
    raw = raw.strip().lower()
    return _LOOKUP.get(raw)


# ── Exchange rate fetching ─────────────────────────────────────────────────

_RATE_CACHE: dict[str, float] = {}   # "USD_UZS" → rate


async def convert_amount(amount: float, from_cur: str, to_cur: str) -> float | None:
    """Convert amount from from_cur to to_cur. Returns None on failure."""
    if from_cur == to_cur:
        return amount

    cache_key = f"{from_cur}_{to_cur}"
    if cache_key in _RATE_CACHE:
        return amount * _RATE_CACHE[cache_key]

    rate = await _fetch_rate(from_cur, to_cur)
    if rate is None:
        return None
    _RATE_CACHE[cache_key] = rate
    return amount * rate


async def _fetch_rate(from_cur: str, to_cur: str) -> float | None:
    """Fetch live exchange rate. Uses exchangerate-api.com free tier."""
    if not CURRENCY_API_KEY:
        # fallback: try open.er-api.com (no key needed, limited)
        url = f"https://open.er-api.com/v6/latest/{from_cur}"
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                    data = await r.json()
                    return data.get("rates", {}).get(to_cur)
        except Exception:
            return None

    url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/pair/{from_cur}/{to_cur}"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                data = await r.json()
                return data.get("conversion_rate")
    except Exception:
        return None
