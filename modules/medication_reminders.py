import datetime

from modules.medication_stock import administer_medication
from utils.id_generator import assign_reminder_id
from utils.json_storage import load_data, save_data


DATETIME_FORMAT = "%Y-%m-%d %H:%M"
DEFAULT_SNOOZE_MINUTES = 5


def _load_reminders():
    return load_data("data/reminders.json")


def _save_reminders(reminders):
    save_data("data/reminders.json", reminders)


def _parse_datetime(value):
    return datetime.datetime.strptime(value.strip(), DATETIME_FORMAT)


def _get_frequency_minutes(reminder):
    if "frequency_minutes" in reminder:
        return int(reminder["frequency_minutes"])

    if "frequency_hours" in reminder:
        return int(reminder["frequency_hours"]) * 60

    return 0


def _normalise_reminder(reminder):
    reminder_copy = dict(reminder)
    reminder_copy["frequency_minutes"] = _get_frequency_minutes(reminder)
    reminder_copy.pop("frequency_hours", None)
    return reminder_copy


def list_reminders(due_only=False):
    reminders = _load_reminders()
    items = [_normalise_reminder(reminder) for reminder in reminders.values()]

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


def get_reminder(reminder_id):
    reminders = _load_reminders()

    if reminder_id not in reminders:
        raise ValueError("Reminder not found.")

    return _normalise_reminder(reminders[reminder_id])


def add_reminder(patient_id, medication_id, dosage, frequency_minutes, next_due, notes=""):
    patients = load_data("data/patients.json")
    medications = load_data("data/medications.json")
    reminders = _load_reminders()

    if patient_id not in patients:
        raise ValueError("Patient not found.")

    if medication_id not in medications:
        raise ValueError("Medication not found.")

    if dosage <= 0:
        raise ValueError("Dosage must be greater than 0.")

    if frequency_minutes <= 0:
        raise ValueError("Frequency must be greater than 0 minutes.")

    next_due_dt = _parse_datetime(next_due)
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
    return _normalise_reminder(reminder)


def administer_reminder(reminder_id):
    reminders = _load_reminders()

    if reminder_id not in reminders:
        raise ValueError("Reminder not found.")

    reminder = reminders[reminder_id]
    frequency_minutes = _get_frequency_minutes(reminder)
    administered_at = datetime.datetime.now()

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
    return _normalise_reminder(reminder), medication, patient


def mark_reminder_completed(reminder_id):
    reminder, _medication, _patient = administer_reminder(reminder_id)
    return reminder


def snooze_reminder(reminder_id, delay_minutes=DEFAULT_SNOOZE_MINUTES):
    reminders = _load_reminders()

    if reminder_id not in reminders:
        raise ValueError("Reminder not found.")

    if delay_minutes <= 0:
        raise ValueError("Snooze delay must be greater than 0 minutes.")

    reminder = reminders[reminder_id]
    reminder["next_due"] = (
        datetime.datetime.now() + datetime.timedelta(minutes=delay_minutes)
    ).strftime(DATETIME_FORMAT)
    reminders[reminder_id] = reminder
    _save_reminders(reminders)
    return _normalise_reminder(reminder)


def toggle_reminder(reminder_id):
    reminders = _load_reminders()

    if reminder_id not in reminders:
        raise ValueError("Reminder not found.")

    reminder = reminders[reminder_id]
    reminder["active"] = not reminder.get("active", True)
    reminders[reminder_id] = reminder
    _save_reminders(reminders)
    return _normalise_reminder(reminder)


def delete_reminder(reminder_id):
    reminders = _load_reminders()

    if reminder_id not in reminders:
        raise ValueError("Reminder not found.")

    reminder = reminders.pop(reminder_id)
    _save_reminders(reminders)
    return _normalise_reminder(reminder)
