#!/usr/bin/env python3
"""Monitor script for weekend-only crypto monitoring.
Returns current timestamp on weekends (triggers agent run),
returns constant string on weekdays (suppresses agent run).
"""
from datetime import datetime, timedelta, timezone

tz = timezone(timedelta(hours=-3))
now = datetime.now(tz)
weekday = now.weekday()  # 0=Monday, 6=Sunday

if weekday >= 5:  # Saturday (5) or Sunday (6)
    # Weekend: return timestamp to trigger agent
    print(now.strftime("%Y-%m-%d %H:%M:%S ARG"))
else:
    # Weekday: return constant to suppress
    print("WEEKDAY_SUPPRESS")
