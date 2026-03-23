import datetime

from utils.id_generator import assign_availability_id
from utils.json_storage import load_data, save_data


DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
BOOKING_DATETIME_FORMAT = "%Y-%m-%d %H:%M"


def _load_availability():
    return load_data("data/staff_availability.json")


def _save_availability(availability):
    save_data("data/staff_availability.json", availability)


def _parse_time(value):
    return datetime.datetime.strptime(value.strip(), TIME_FORMAT)


def _parse_shift_bounds(record):
    shift_start = datetime.datetime.strptime(
        f'{record["shift_date"]} {record["shift_start"]}',
        BOOKING_DATETIME_FORMAT,
    )
    shift_end = datetime.datetime.strptime(
        f'{record["shift_date"]} {record["shift_end"]}',
        BOOKING_DATETIME_FORMAT,
    )
    return shift_start, shift_end


def get_staff_status(staff_id, at_time=None, availability=None, bookings=None):
    if at_time is None:
        at_time = datetime.datetime.now()

    if availability is None:
        availability = _load_availability()

    if bookings is None:
        bookings = load_data("data/bookings.json")

    on_shift = False

    for record in availability.values():
        if record["staff_id"] != staff_id:
            continue

        shift_start, shift_end = _parse_shift_bounds(record)
        if shift_start <= at_time < shift_end:
            on_shift = True
            break

    if not on_shift:
        return "On Leave"

    for booking in bookings.values():
        if booking["staff_id"] != staff_id:
            continue

        booking_start = datetime.datetime.strptime(
            booking["start_time"],
            BOOKING_DATETIME_FORMAT,
        )
        booking_end = datetime.datetime.strptime(
            booking["end_time"],
            BOOKING_DATETIME_FORMAT,
        )

        if booking_start <= at_time < booking_end:
            return "Unavailable"

    return "Available"


def validate_staff_booking(staff_id, start_time, end_time, ignore_booking_id=None):
    availability = _load_availability()
    bookings = load_data("data/bookings.json")

    if isinstance(start_time, datetime.datetime):
        start_dt = start_time
    else:
        start_dt = datetime.datetime.strptime(start_time.strip(), BOOKING_DATETIME_FORMAT)

    if isinstance(end_time, datetime.datetime):
        end_dt = end_time
    else:
        end_dt = datetime.datetime.strptime(end_time.strip(), BOOKING_DATETIME_FORMAT)

    on_shift = False
    for record in availability.values():
        if record["staff_id"] != staff_id:
            continue

        shift_start, shift_end = _parse_shift_bounds(record)
        if shift_start <= start_dt and end_dt <= shift_end:
            on_shift = True
            break

    if not on_shift:
        raise ValueError("Staff member is outside their scheduled shift for that booking.")

    for booking in bookings.values():
        if booking["staff_id"] != staff_id:
            continue

        if ignore_booking_id and booking["booking_id"] == ignore_booking_id:
            continue

        booking_start = datetime.datetime.strptime(
            booking["start_time"],
            BOOKING_DATETIME_FORMAT,
        )
        booking_end = datetime.datetime.strptime(
            booking["end_time"],
            BOOKING_DATETIME_FORMAT,
        )

        if start_dt < booking_end and end_dt > booking_start:
            raise ValueError("Staff member is already booked into another room during that time.")

    return True


def list_availability(reference_time=None):
    availability = _load_availability()
    bookings = load_data("data/bookings.json")
    items = []

    for record in availability.values():
        record_copy = dict(record)
        record_copy["status"] = get_staff_status(
            record["staff_id"],
            at_time=reference_time,
            availability=availability,
            bookings=bookings,
        )
        items.append(record_copy)

    return sorted(
        items,
        key=lambda item: (item["shift_date"], item["shift_start"], item["staff_name"]),
    )


def add_availability(staff_id, shift_date, shift_start, shift_end, notes=""):
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
        "status": "Available",
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
