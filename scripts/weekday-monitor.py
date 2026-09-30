#!/usr/bin/env python3
"""Monitor script for weekday crypto monitoring (every 30min Mon-Fri).
Returns timestamp on weekdays (triggers agent every 30min),
returns constant on weekends (suppresses agent).
"""
from datetime import datetime, timedelta, timezone

tz = timezone(timedelta(hours=-3))
now = datetime.now(tz)
weekday = now.weekday()  # 0=Monday, 6=Sunday

if weekday < 5:  # Monday to Friday
    # Weekday: return timestamp to trigger agent
    print(now.strftime("%Y-%m-%d %H:%M:%S ARG"))
else:
    # Weekend: return constant to suppress
    print("WEEKEND_SUPPRESS")
