"""OpenAI API wrapper."""
from __future__ import annotations

import logging

from bot.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)


async def call_openai(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> str | None:
    """Call OpenAI chat completion. Returns text or None on failure."""
    if not OPENAI_API_KEY:
        return "⚠️ OpenAI API key not configured."
    try:
        import openai
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system",  "content": system_prompt},
                {"role": "user",    "content": user_prompt},
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error("OpenAI error: %s", e)
        return None
