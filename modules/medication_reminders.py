import datetime

from utils.id_generator import assign_reminder_id
from utils.json_storage import load_data, save_data


DATETIME_FORMAT = "%Y-%m-%d %H:%M"


def _load_reminders():
    return load_data("data/reminders.json")


def _save_reminders(reminders):
    save_data("data/reminders.json", reminders)


def _parse_datetime(value):
    return datetime.datetime.strptime(value.strip(), DATETIME_FORMAT)


def list_reminders(due_only=False):
    reminders = _load_reminders()
    items = list(reminders.values())

    if due_only:
        now = datetime.datetime.now()
        items = [
            reminder
            for reminder in items
            if reminder.get("active", True)
            and _parse_datetime(reminder["next_due"]) <= now
        ]

    items.sort(key=lambda reminder: reminder["next_due"])
    return items


def add_reminder(patient_id, medication_id, dosage, frequency_hours, next_due, notes=""):
    patients = load_data("data/patients.json")
    medications = load_data("data/medications.json")
    reminders = _load_reminders()

    if patient_id not in patients:
        raise ValueError("Patient not found.")

    if medication_id not in medications:
        raise ValueError("Medication not found.")

    if dosage <= 0:
        raise ValueError("Dosage must be greater than 0.")

    if frequency_hours <= 0:
        raise ValueError("Frequency must be greater than 0 hours.")

    next_due_dt = _parse_datetime(next_due)
    reminder_id = assign_reminder_id(reminders)

    reminder = {
        "reminder_id": reminder_id,
        "patient_id": patient_id,
        "medication_id": medication_id,
        "medication_name": medications[medication_id]["name"],
        "dosage": dosage,
        "frequency_hours": frequency_hours,
        "next_due": next_due_dt.strftime(DATETIME_FORMAT),
        "notes": notes.strip(),
        "active": True,
    }

    reminders[reminder_id] = reminder
    _save_reminders(reminders)
    return reminder


def mark_reminder_completed(reminder_id):
    reminders = _load_reminders()

    if reminder_id not in reminders:
        raise ValueError("Reminder not found.")

    reminder = reminders[reminder_id]
    next_due = _parse_datetime(reminder["next_due"]) + datetime.timedelta(
        hours=int(reminder["frequency_hours"])
    )
    reminder["next_due"] = next_due.strftime(DATETIME_FORMAT)
    _save_reminders(reminders)
    return reminder


def toggle_reminder(reminder_id):
    reminders = _load_reminders()

    if reminder_id not in reminders:
        raise ValueError("Reminder not found.")

    reminder = reminders[reminder_id]
    reminder["active"] = not reminder.get("active", True)
    _save_reminders(reminders)
    return reminder


def delete_reminder(reminder_id):
    reminders = _load_reminders()

    if reminder_id not in reminders:
        raise ValueError("Reminder not found.")

    reminder = reminders.pop(reminder_id)
    _save_reminders(reminders)
    return reminder
