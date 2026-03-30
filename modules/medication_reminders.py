import datetime
from zoneinfo import ZoneInfo

from modules.medication_stock import administer_medication, validate_dosage
from utils.id_generator import assign_reminder_id
from utils.json_storage import load_data, save_data


# This file manages repeat medication reminders.
APP_TIMEZONE = ZoneInfo("Europe/London")
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
DEFAULT_SNOOZE_MINUTES = 5
MAX_NEXT_DUE_MINUTES = 60
MAX_DELAY_MINUTES = 30


def _load_reminders():
    # Read reminder records from storage.
    return load_data("data/reminders.json")


def _save_reminders(reminders):
    # Save updated reminder data.
    save_data("data/reminders.json", reminders)


def _parse_datetime(value):
    # Convert saved reminder date text into a datetime object.
    return datetime.datetime.strptime(value.strip(), DATETIME_FORMAT).replace(
        tzinfo=APP_TIMEZONE
    )


def _parse_next_due_input(value):
    # The GUI now captures the first due time as minutes from now.
    cleaned = value.strip()

    if not cleaned:
        raise ValueError("Next due is required.")

    if not cleaned.isdigit():
        raise ValueError("Next due must be entered in minutes only.")

    minutes = int(cleaned)

    if minutes <= 0:
        raise ValueError("Next due must be greater than 0 minutes.")

    if minutes > MAX_NEXT_DUE_MINUTES:
        raise ValueError("Next due cannot be more than 60 minutes from now.")

    return datetime.datetime.now(APP_TIMEZONE) + datetime.timedelta(minutes=minutes)


def list_reminders(due_only=False):
    # Return all reminders, or only the ones that are currently due.
    reminders = _load_reminders()
    items = [dict(reminder) for reminder in reminders.values()]

    if due_only:
        now = datetime.datetime.now(APP_TIMEZONE)
        items = [
            reminder
            for reminder in items
            if reminder.get("active", True)
            and _parse_datetime(reminder["next_due"]) <= now
        ]

    items.sort(key=lambda reminder: reminder["next_due"])
    return items


def get_reminder(reminder_id):
    # Return one reminder record.
    reminders = _load_reminders()

    if reminder_id not in reminders:
        raise ValueError("Reminder not found.")

    return dict(reminders[reminder_id])


def add_reminder(patient_id, medication_id, dosage, frequency_minutes, next_due, notes=""):
    # Create a new reminder and save the medication, patient, dosage, and next due time.
    patients = load_data("data/patients.json")
    medications = load_data("data/medications.json")
    reminders = _load_reminders()

    if patient_id not in patients:
        raise ValueError("Patient not found.")

    if medication_id not in medications:
        raise ValueError("Medication not found.")

    validate_dosage(dosage)

    if frequency_minutes <= 0:
        raise ValueError("Frequency must be greater than 0 minutes.")

    next_due_dt = _parse_next_due_input(next_due)
    reminder_id = assign_reminder_id(reminders)

    reminder = {
        "reminder_id": reminder_id,
        "patient_id": patient_id,
        "medication_id": medication_id,
        "medication_name": medications[medication_id]["name"],
        "dosage": dosage,
        "frequency_minutes": frequency_minutes,
        "next_due": next_due_dt.strftime(DATETIME_FORMAT),
        "notes": notes.strip(),
        "active": True,
    }

    reminders[reminder_id] = reminder
    _save_reminders(reminders)
    return dict(reminder)


def administer_reminder(reminder_id):
    # Give the medication now, reduce stock, and move the reminder forward.
    reminders = _load_reminders()

    if reminder_id not in reminders:
        raise ValueError("Reminder not found.")

    reminder = reminders[reminder_id]
    if not reminder.get("active", True):
        raise ValueError("Reminder is not active.")

    next_due_dt = _parse_datetime(reminder["next_due"])
    now = datetime.datetime.now(APP_TIMEZONE)

    if next_due_dt > now:
        raise ValueError(
            f'Reminder is not due yet. Next due time is {reminder["next_due"]}.'
        )

    frequency_minutes = int(reminder["frequency_minutes"])
    administered_at = now

    medication, patient = administer_medication(
        reminder["medication_id"],
        reminder["patient_id"],
        int(reminder["dosage"]),
    )

    reminder["medication_name"] = medication["name"]
    reminder["frequency_minutes"] = frequency_minutes
    reminder["next_due"] = (
        administered_at + datetime.timedelta(minutes=frequency_minutes)
    ).strftime(DATETIME_FORMAT)
    reminder["last_administered_at"] = administered_at.strftime(DATETIME_FORMAT)

    reminders[reminder_id] = reminder
    _save_reminders(reminders)
    return dict(reminder), medication, patient


def mark_reminder_completed(reminder_id):
    # Older name kept for compatibility. It now just administers the reminder.
    reminder, _medication, _patient = administer_reminder(reminder_id)
    return reminder


def snooze_reminder(reminder_id, delay_minutes=DEFAULT_SNOOZE_MINUTES):
    # Push the reminder forward by a small amount of time.
    reminders = _load_reminders()

    if reminder_id not in reminders:
        raise ValueError("Reminder not found.")

    if delay_minutes <= 0:
        raise ValueError("Snooze delay must be greater than 0 minutes.")

    if delay_minutes > MAX_DELAY_MINUTES:
        raise ValueError(
            f"Snooze delay cannot be more than {MAX_DELAY_MINUTES} minutes."
        )

    reminder = reminders[reminder_id]
    reminder["next_due"] = (
        datetime.datetime.now(APP_TIMEZONE) + datetime.timedelta(minutes=delay_minutes)
    ).strftime(DATETIME_FORMAT)
    reminders[reminder_id] = reminder
    _save_reminders(reminders)
    return dict(reminder)


def toggle_reminder(reminder_id):
    # Pause or resume a reminder.
    reminders = _load_reminders()

    if reminder_id not in reminders:
        raise ValueError("Reminder not found.")

    reminder = reminders[reminder_id]
    reminder["active"] = not reminder.get("active", True)
    reminders[reminder_id] = reminder
    _save_reminders(reminders)
    return dict(reminder)


def delete_reminder(reminder_id):
    # Remove a reminder from the system.
    reminders = _load_reminders()

    if reminder_id not in reminders:
        raise ValueError("Reminder not found.")

    reminder = reminders.pop(reminder_id)
    _save_reminders(reminders)
    return dict(reminder)
