import datetime

from utils.id_generator import assign_patient_id
from utils.json_storage import load_data, save_data


DATE_FORMAT = "%Y-%m-%d"


def _load_patients():
    return load_data("data/patients.json")


def _save_patients(patients):
    save_data("data/patients.json", patients)


def _ensure_patient_exists(patients, patient_id):
    if patient_id not in patients:
        raise ValueError("Patient not found.")


def _validate_patient_fields(first_name, last_name, dob):
    if not first_name.strip():
        raise ValueError("First name is required.")

    if not last_name.strip():
        raise ValueError("Last name is required.")

    try:
        datetime.datetime.strptime(dob.strip(), DATE_FORMAT)
    except ValueError as exc:
        raise ValueError("Date of birth must use YYYY-MM-DD.") from exc


def list_patients(search_text=""):
    patients = _load_patients()
    items = list(patients.values())

    if search_text:
        query = search_text.strip().lower()
        items = [
            patient
            for patient in items
            if query in patient.get("patient_id", "").lower()
            or query in patient.get("first_name", "").lower()
            or query in patient.get("last_name", "").lower()
            or query in patient.get("condition", "").lower()
        ]

    return sorted(items, key=lambda patient: patient["patient_id"])


def get_patient(patient_id):
    patients = _load_patients()
    _ensure_patient_exists(patients, patient_id)
    return patients[patient_id]


def add_patient(first_name, last_name, email, phone, dob, condition, medication, notes=""):
    _validate_patient_fields(first_name, last_name, dob)

    patients = _load_patients()
    patient_id = assign_patient_id(patients)
    timestamp = str(datetime.datetime.now())

    patient_data = {
        "patient_id": patient_id,
        "first_name": first_name.strip().title(),
        "last_name": last_name.strip().title(),
        "email": email.strip(),
        "phone": phone.strip(),
        "dob": dob.strip(),
        "condition": condition.strip(),
        "medication": medication.strip(),
        "notes": notes.strip(),
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    patients[patient_id] = patient_data
    _save_patients(patients)
    return patient_data


def update_patient(patient_id, first_name, last_name, email, phone, dob, condition, medication, notes=""):
    _validate_patient_fields(first_name, last_name, dob)

    patients = _load_patients()
    _ensure_patient_exists(patients, patient_id)

    patient = patients[patient_id]
    patient.update(
        {
            "first_name": first_name.strip().title(),
            "last_name": last_name.strip().title(),
            "email": email.strip(),
            "phone": phone.strip(),
            "dob": dob.strip(),
            "condition": condition.strip(),
            "medication": medication.strip(),
            "notes": notes.strip(),
            "updated_at": str(datetime.datetime.now()),
        }
    )

    _save_patients(patients)
    return patient


def delete_patient(patient_id):
    patients = _load_patients()
    _ensure_patient_exists(patients, patient_id)

    bookings = load_data("data/bookings.json")
    reminders = load_data("data/reminders.json")
    medical_image_records = load_data("data/medical_images.json")

    deleted_patient = patients.pop(patient_id)

    bookings = {
        booking_id: booking
        for booking_id, booking in bookings.items()
        if booking.get("patient_id") != patient_id
    }
    reminders = {
        reminder_id: reminder
        for reminder_id, reminder in reminders.items()
        if reminder.get("patient_id") != patient_id
    }
    medical_image_records = {
        image_id: image
        for image_id, image in medical_image_records.items()
        if image.get("patient_id") != patient_id
    }

    _save_patients(patients)
    save_data("data/bookings.json", bookings)
    save_data("data/reminders.json", reminders)
    save_data("data/medical_images.json", medical_image_records)
    return deleted_patient
