import datetime

from utils.id_generator import assign_patient_id
from utils.json_storage import load_data, save_data


# This file is the patient records backend.
# It validates patient details and saves patient data.
DATE_FORMAT = "%Y-%m-%d"


def _load_patients():
    # Read all patient records from storage.
    return load_data("data/patients.json")


def _save_patients(patients):
    # Save updated patient records.
    save_data("data/patients.json", patients)


def _ensure_patient_exists(patients, patient_id):
    # Stop the program from editing or deleting a patient that is not there.
    if patient_id not in patients:
        raise ValueError("Patient not found.")


def _contains_digits(value):
    # Used by validation rules for fields that should not contain numbers.
    return any(character.isdigit() for character in value)


def _validate_patient_fields(first_name, last_name, email, phone, dob, condition, medication, notes):
    # Check that the patient form has sensible and safe input values.
    if not first_name.strip():
        raise ValueError("First name is required.")

    if not last_name.strip():
        raise ValueError("Last name is required.")

    if _contains_digits(first_name):
        raise ValueError("First name cannot contain numbers.")

    if _contains_digits(last_name):
        raise ValueError("Last name cannot contain numbers.")

    email_value = email.strip().lower()
    if not email_value:
        raise ValueError("Email is required.")

    if not email_value.endswith("@gmail.com") or email_value == "@gmail.com":
        raise ValueError("Email must end with @gmail.com.")

    phone_value = phone.strip()
    if not phone_value:
        raise ValueError("Phone number is required.")

    if not phone_value.isdigit():
        raise ValueError("Phone number must contain numbers only.")

    if _contains_digits(condition):
        raise ValueError("Condition cannot contain numbers.")

    if _contains_digits(medication):
        raise ValueError("Medication cannot contain numbers.")

    if _contains_digits(notes):
        raise ValueError("Notes cannot contain numbers.")

    try:
        datetime.datetime.strptime(dob.strip(), DATE_FORMAT)
    except ValueError as exc:
        raise ValueError("Date of birth must use YYYY-MM-DD.") from exc


def list_patients(search_text=""):
    # Return all patients, or only the ones that match the search box.
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
    # Return one full patient record.
    patients = _load_patients()
    _ensure_patient_exists(patients, patient_id)
    return patients[patient_id]


def add_patient(first_name, last_name, email, phone, dob, condition, medication, notes=""):
    # Create a new patient and give them a unique patient ID.
    _validate_patient_fields(
        first_name,
        last_name,
        email,
        phone,
        dob,
        condition,
        medication,
        notes,
    )

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
    # Save changes to an existing patient record.
    _validate_patient_fields(
        first_name,
        last_name,
        email,
        phone,
        dob,
        condition,
        medication,
        notes,
    )

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
    # Remove the patient and any linked reminders.
    patients = _load_patients()
    _ensure_patient_exists(patients, patient_id)

    reminders = load_data("data/reminders.json")

    deleted_patient = patients.pop(patient_id)

    reminders = {
        reminder_id: reminder
        for reminder_id, reminder in reminders.items()
        if reminder.get("patient_id") != patient_id
    }

    _save_patients(patients)
    save_data("data/reminders.json", reminders)
    return deleted_patient
