import pytz
from datetime import timezone
import apscheduler.util as aps_util

_original_astimezone = aps_util.astimezone

def custom_astimezone(tz):
    # If it's already a pytz timezone, return as-is.
    if hasattr(tz, "zone") and tz.zone in pytz.all_timezones:
        return tz
    # Handle the built-in UTC timezone.
    if tz == timezone.utc:
        return pytz.utc
    # Attempt to convert other timezone types (e.g., zoneinfo.ZoneInfo) to pytz.
    try:
        tz_name = getattr(tz, "key", None)
        if tz_name is None:
            tz_name = str(tz)
        return pytz.timezone(tz_name)
    except Exception:
        raise TypeError('Only timezones from the pytz library are supported')

def initialize_timezone_patch():
    """Patch APScheduler's timezone handling to work with pytz."""
    aps_util.astimezone = custom_astimezone