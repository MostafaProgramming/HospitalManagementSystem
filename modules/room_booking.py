import datetime

from utils.id_generator import assign_booking_id, assign_room_id
from utils.json_storage import load_data, save_data


DATETIME_FORMAT = "%Y-%m-%d %H:%M"


def _load_rooms():
    return load_data("data/rooms.json")


def _save_rooms(rooms):
    save_data("data/rooms.json", rooms)


def _load_bookings():
    return load_data("data/bookings.json")


def _save_bookings(bookings):
    save_data("data/bookings.json", bookings)


def _parse_datetime(value):
    if isinstance(value, datetime.datetime):
        return value
    return datetime.datetime.strptime(value.strip(), DATETIME_FORMAT)


def get_room_status(room_id, at_time=None, rooms=None, bookings=None):
    if at_time is None:
        at_time = datetime.datetime.now()

    if rooms is None:
        rooms = _load_rooms()

    if bookings is None:
        bookings = _load_bookings()

    for booking in bookings.values():
        if booking["room_id"] != room_id:
            continue

        booking_start = _parse_datetime(booking["start_time"])
        booking_end = _parse_datetime(booking["end_time"])

        if booking_start <= at_time < booking_end:
            return "Unavailable"

    room = rooms.get(room_id, {})
    return room.get("status", "Available")


def list_rooms(reference_time=None):
    rooms = _load_rooms()
    bookings = _load_bookings()
    room_items = []

    for room in rooms.values():
        room_copy = dict(room)
        room_copy["status"] = get_room_status(
            room["room_id"],
            at_time=reference_time,
            rooms=rooms,
            bookings=bookings,
        )
        room_items.append(room_copy)

    return sorted(room_items, key=lambda room: room["room_id"])


def add_room(room_label, room_type, capacity, notes="", status="Available"):
    if not room_label.strip():
        raise ValueError("Room label is required.")

    if capacity <= 0:
        raise ValueError("Capacity must be greater than 0.")

    rooms = _load_rooms()
    room_id = assign_room_id(rooms)

    room = {
        "room_id": room_id,
        "room_label": room_label.strip().upper(),
        "room_type": room_type.strip().title() or "General",
        "capacity": int(capacity),
        "notes": notes.strip(),
        "status": status.strip().title() or "Available",
    }

    rooms[room_id] = room
    _save_rooms(rooms)
    return room


def delete_room(room_id):
    rooms = _load_rooms()
    bookings = _load_bookings()

    if room_id not in rooms:
        raise ValueError("Room not found.")

    for booking in bookings.values():
        if booking["room_id"] == room_id:
            raise ValueError("Cancel this room's bookings before deleting it.")

    room = rooms.pop(room_id)
    _save_rooms(rooms)
    return room


def list_bookings(room_id=None, upcoming_only=False):
    bookings = _load_bookings()
    items = list(bookings.values())

    if room_id:
        items = [booking for booking in items if booking["room_id"] == room_id]

    if upcoming_only:
        now = datetime.datetime.now()
        items = [
            booking
            for booking in items
            if _parse_datetime(booking["end_time"]) >= now
        ]

    items.sort(key=lambda booking: booking["start_time"])
    return items


def is_room_available(room_id, start_time, end_time, ignore_booking_id=None):
    start_dt = _parse_datetime(start_time)
    end_dt = _parse_datetime(end_time)

    if end_dt <= start_dt:
        raise ValueError("End time must be after start time.")

    if start_dt.date() != end_dt.date():
        raise ValueError("Bookings must start and end on the same day.")

    bookings = _load_bookings()

    for booking in bookings.values():
        if booking["room_id"] != room_id:
            continue

        if ignore_booking_id and booking["booking_id"] == ignore_booking_id:
            continue

        booking_start = _parse_datetime(booking["start_time"])
        booking_end = _parse_datetime(booking["end_time"])

        if start_dt < booking_end and end_dt > booking_start:
            return False

    return True


def list_available_rooms(start_time, end_time):
    start_dt = _parse_datetime(start_time)
    end_dt = _parse_datetime(end_time)
    available = []

    for room in list_rooms():
        if is_room_available(room["room_id"], start_dt, end_dt):
            available.append(room)

    return available


def create_booking(room_id, staff_id, patient_id, start_time, end_time, purpose="Consultation"):
    rooms = _load_rooms()
    patients = load_data("data/patients.json")
    users = load_data("data/users.json")
    bookings = _load_bookings()

    if room_id not in rooms:
        raise ValueError("Room not found.")

    if patient_id not in patients:
        raise ValueError("Patient not found.")

    user_ids = {user["userID"] for user in users.values()}
    if staff_id not in user_ids:
        raise ValueError("Staff ID not found.")

    start_dt = _parse_datetime(start_time)
    end_dt = _parse_datetime(end_time)

    if not is_room_available(room_id, start_dt, end_dt):
        raise ValueError("Room is not available during the selected time.")

    booking_id = assign_booking_id(bookings)
    booking = {
        "booking_id": booking_id,
        "room_id": room_id,
        "staff_id": staff_id,
        "patient_id": patient_id,
        "purpose": purpose.strip() or "Consultation",
        "start_time": start_dt.strftime(DATETIME_FORMAT),
        "end_time": end_dt.strftime(DATETIME_FORMAT),
    }

    bookings[booking_id] = booking
    _save_bookings(bookings)
    return booking


def cancel_booking(booking_id):
    bookings = _load_bookings()

    if booking_id not in bookings:
        raise ValueError("Booking not found.")

    booking = bookings.pop(booking_id)
    _save_bookings(bookings)
    return booking
