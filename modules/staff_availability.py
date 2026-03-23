import datetime

from utils.id_generator import assign_availability_id
from utils.json_storage import load_data, save_data


DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"


def _load_availability():
    return load_data("data/staff_availability.json")


def _save_availability(availability):
    save_data("data/staff_availability.json", availability)


def _parse_time(value):
    return datetime.datetime.strptime(value.strip(), TIME_FORMAT)


def list_availability():
    availability = _load_availability()
    return sorted(
        availability.values(),
        key=lambda item: (item["shift_date"], item["shift_start"], item["staff_name"]),
    )


def add_availability(staff_id, shift_date, shift_start, shift_end, status="Available", notes=""):
    users = load_data("data/users.json")
    availability = _load_availability()

    matched_user = None
    for user in users.values():
        if user["userID"] == staff_id:
            matched_user = user
            break

    if not matched_user:
        raise ValueError("Staff ID not found.")

    try:
        datetime.datetime.strptime(shift_date.strip(), DATE_FORMAT)
    except ValueError as exc:
        raise ValueError("Shift date must use YYYY-MM-DD.") from exc

    start_time = _parse_time(shift_start)
    end_time = _parse_time(shift_end)

    if end_time <= start_time:
        raise ValueError("Shift end must be after shift start.")

    for record in availability.values():
        if record["staff_id"] != staff_id or record["shift_date"] != shift_date.strip():
            continue

        record_start = _parse_time(record["shift_start"])
        record_end = _parse_time(record["shift_end"])

        if start_time < record_end and end_time > record_start:
            raise ValueError("This shift overlaps with an existing availability record.")

    availability_id = assign_availability_id(availability)
    record = {
        "availability_id": availability_id,
        "staff_id": matched_user["userID"],
        "staff_name": matched_user["username"],
        "role": matched_user["role"],
        "shift_date": shift_date.strip(),
        "shift_start": start_time.strftime(TIME_FORMAT),
        "shift_end": end_time.strftime(TIME_FORMAT),
        "status": status.strip().title() or "Available",
        "notes": notes.strip(),
    }

    availability[availability_id] = record
    _save_availability(availability)
    return record


def delete_availability(availability_id):
    availability = _load_availability()

    if availability_id not in availability:
        raise ValueError("Availability record not found.")

    record = availability.pop(availability_id)
    _save_availability(availability)
    return record
