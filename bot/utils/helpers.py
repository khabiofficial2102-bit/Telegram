"""Shared utility functions."""
from __future__ import annotations

import re
from datetime import datetime, date, timedelta


def parse_datetime_text(raw: str) -> tuple[datetime | None, str]:
    """
    Parse reminder / plan input.
    Supported formats:
      - "YYYY-MM-DD HH:MM text"
      - "HH:MM text"   → today's date
    Returns (datetime_obj, text) or (None, raw) on failure.
    """
    raw = raw.strip()

    # Full datetime
    m = re.match(r"^(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2})\s+(.+)$", raw, re.DOTALL)
    if m:
        try:
            dt_str = f"{m.group(1)} {m.group(2)}"
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            return dt, m.group(3).strip()
        except ValueError:
            pass

    # Time only → today
    m = re.match(r"^(\d{1,2}:\d{2})\s+(.+)$", raw, re.DOTALL)
    if m:
        try:
            today = date.today().isoformat()
            dt = datetime.strptime(f"{today} {m.group(1)}", "%Y-%m-%d %H:%M")
            return dt, m.group(2).strip()
        except ValueError:
            pass

    return None, raw


def parse_time(raw: str) -> str | None:
    """Return 'HH:MM' string or None."""
    m = re.match(r"^(\d{1,2}:\d{2})$", raw.strip())
    if m:
        try:
            datetime.strptime(m.group(1), "%H:%M")
            return m.group(1)
        except ValueError:
            pass
    return None


def period_range(period: str) -> tuple[datetime, datetime]:
    """Return (start, end) UTC datetimes for a named period."""
    now = datetime.utcnow()
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end   = start + timedelta(days=1)
    elif period == "week":
        start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end   = start + timedelta(days=7)
    elif period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # next month
        if now.month == 12:
            end = now.replace(year=now.year + 1, month=1, day=1,
                              hour=0, minute=0, second=0, microsecond=0)
        else:
            end = now.replace(month=now.month + 1, day=1,
                              hour=0, minute=0, second=0, microsecond=0)
    elif period == "year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end   = now.replace(year=now.year + 1, month=1, day=1,
                            hour=0, minute=0, second=0, microsecond=0)
    else:
        start = datetime.min
        end   = datetime.max
    return start, end
