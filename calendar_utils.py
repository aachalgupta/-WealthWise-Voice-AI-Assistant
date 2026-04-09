"""
calendar_utils.py
Google Calendar integration for WealthWise Advisory.
"""

import os
import datetime
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Calendar API scope
SCOPES = ["https://www.googleapis.com/auth/calendar"]
IST    = ZoneInfo("Asia/Kolkata")

# Appointment duration in minutes
APPOINTMENT_DURATION = 30

# Working hours (IST)
WORK_START_HOUR = 9
WORK_END_HOUR   = 19  # 7 PM

# How many days ahead to check for slots
DAYS_AHEAD = 2


def get_calendar_service():
    """Authenticate and return Google Calendar service."""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def get_available_slots(num_slots: int = 3, day_filter: str = "any") -> list[dict]:
    """
    Fetch next N available 30-minute slots from Google Calendar.
    day_filter: "today", "tomorrow", or "any"
    """
    service = get_calendar_service()

    now        = datetime.datetime.now(IST)
    time_min   = now.isoformat()
    time_max   = (now + datetime.timedelta(days=DAYS_AHEAD)).isoformat()

    events_result = service.events().list(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    existing_events = events_result.get("items", [])

    busy_intervals = []
    for event in existing_events:
        start = event["start"].get("dateTime")
        end   = event["end"].get("dateTime")
        if start and end:
            busy_intervals.append((
                datetime.datetime.fromisoformat(start),
                datetime.datetime.fromisoformat(end),
            ))

    available_slots = []
    check_time = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    now_date = now.date()  

    while len(available_slots) < num_slots:
        if day_filter == "today" and check_time.date() != now_date:
            break
        if day_filter == "tomorrow":
            tomorrow = now_date + datetime.timedelta(days=1)
            if check_time.date() < tomorrow:
                check_time += datetime.timedelta(minutes=30)
                continue
            if check_time.date() > tomorrow:
                break

        if check_time.weekday() == 6:
            check_time += datetime.timedelta(days=1)
            check_time = check_time.replace(hour=WORK_START_HOUR, minute=0)
            continue

        if check_time.hour < WORK_START_HOUR:
            check_time = check_time.replace(hour=WORK_START_HOUR, minute=0)

        if check_time.hour >= WORK_END_HOUR:
            check_time += datetime.timedelta(days=1)
            check_time = check_time.replace(hour=WORK_START_HOUR, minute=0)
            continue

        slot_end = check_time + datetime.timedelta(minutes=APPOINTMENT_DURATION)

        is_busy = any(
            not (slot_end <= busy_start or check_time >= busy_end)
            for busy_start, busy_end in busy_intervals
        )

        if not is_busy:
            available_slots.append({
                "start":         check_time,
                "end":           slot_end,
                "display":       check_time.strftime("%A, %d %B at %I:%M %p IST"),
                "start_iso":     check_time.isoformat(),
                "end_iso":       slot_end.isoformat(),
            })

        check_time += datetime.timedelta(minutes=30)

    return available_slots

def book_appointment(
    name:        str,
    email:       str,
    phone:       str,
    slot_start:  str,
    slot_end:    str,
    slot_display: str,
) -> dict:
    """
    Book an appointment on Google Calendar.
    Creates an event and sends email invite to the user.
    Returns confirmation details.
    """
    service = get_calendar_service()

    event = {
        "summary": f"WealthWise Advisory — {name}",
        "description": (
            f"Financial Advisory Session\n\n"
            f"Client: {name}\n"
            f"Phone: {phone}\n"
            f"Email: {email}\n\n"
            f"This is a free 30-minute discovery call with a WealthWise financial advisor."
        ),
        "start": {
            "dateTime": slot_start,
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": slot_end,
            "timeZone": "Asia/Kolkata",
        },
        "attendees": [
            {"email": email, "displayName": name},
        ],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email",  "minutes": 60},
                {"method": "popup",  "minutes": 15},
            ],
        },
        "conferenceData": {
            "createRequest": {
                "requestId":             f"wealthwise-{name}-{slot_start}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event,
        sendUpdates="all",          # sends email invite to attendee
        conferenceDataVersion=1,    # creates Google Meet link
    ).execute()

    meet_link = (
        created_event
        .get("conferenceData", {})
        .get("entryPoints", [{}])[0]
        .get("uri", "")
    )

    return {
        "event_id":    created_event["id"],
        "event_link":  created_event.get("htmlLink", ""),
        "meet_link":   meet_link,
        "slot_display": slot_display,
        "name":        name,
        "email":       email,
        "phone":       phone,
    }


if __name__ == "__main__":
    # Test: print next 3 available slots
    print("Fetching available slots...\n")
    slots = get_available_slots(3)
    for i, slot in enumerate(slots, 1):
        print(f"Slot {i}: {slot['display']}")
