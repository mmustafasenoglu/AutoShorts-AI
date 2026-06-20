import json
import os
from datetime import datetime, timezone, timedelta

SLOTS = [10, 15, 20] # 10:00, 15:00, 20:00
STATE_FILE = "scheduled_slots.json"

def get_istanbul_now():
    # UTC+3
    return datetime.now(timezone(timedelta(hours=3)))

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                return data.get("last_scheduled", None)
        except:
            return None
    return None

def save_state(iso_str):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_scheduled": iso_str}, f)

def get_next_slot():
    """
    Returns (local_publish_time_datetime, utc_publish_time_iso_string)
    """
    now = get_istanbul_now()
    last_scheduled_iso = load_state()
    
    # Define our starting point for calculating the next slot
    if last_scheduled_iso:
        # Parse it
        try:
            last_dt = datetime.fromisoformat(last_scheduled_iso)
            # Ensure it is timezone aware
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=timezone(timedelta(hours=3)))
                
            # If the last scheduled time is in the past, ignore it
            if last_dt < now:
                base_time = now
            else:
                base_time = last_dt
        except:
            base_time = now
    else:
        base_time = now

    # Now find the next slot after base_time
    candidate_date = base_time.date()
    
    # If base_time is exactly on a slot, we need to pick the *next* slot.
    # So we add a tiny bit of time to ensure we move forward.
    base_time_plus_minute = base_time + timedelta(minutes=1)
    
    while True:
        for slot_hour in SLOTS:
            candidate_dt = datetime(
                year=candidate_date.year,
                month=candidate_date.month,
                day=candidate_date.day,
                hour=slot_hour,
                minute=0,
                second=0,
                tzinfo=timezone(timedelta(hours=3))
            )
            if candidate_dt >= base_time_plus_minute:
                # Found the next slot!
                # Save it so the next call gets the one after this
                save_state(candidate_dt.isoformat())
                
                # Calculate UTC ISO for YouTube
                publish_utc = candidate_dt.astimezone(timezone.utc)
                publish_at_iso = publish_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                return candidate_dt, publish_at_iso
                
        # If we exhausted all slots for candidate_date, move to the next day
        candidate_date += timedelta(days=1)
