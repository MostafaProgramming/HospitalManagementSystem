import datetime

from utils.id_generator import assign_medication_id
from utils.json_storage import load_data, save_data


def _load_medications():
    return load_data("data/medications.json")


def _save_medications(medications):
    save_data("data/medications.json", medications)


def list_medications(low_stock_only=False):
    medications = load_data("data/medications.json")
    items = list(medications.values())

    if low_stock_only:
        items = [
            medication
            for medication in items
            if medication["currentQty"] <= medication["reorderLevel"]
        ]

    return sorted(items, key=lambda medication: medication["id"])


def get_medication(medication_id):
    medications = _load_medications()
    if medication_id not in medications:
        raise ValueError("Medication not found.")
    return medications[medication_id]


def add_medication(name, category, description, max_stock, reorder_level, initial_qty=None):
    name = name.strip()
    category = category.strip()
    description = description.strip()

    if not name:
        raise ValueError("Medication name is required.")

    if max_stock <= 0:
        raise ValueError("Maximum stock must be greater than 0.")

    if reorder_level < 0:
        raise ValueError("Reorder level cannot be negative.")

    if reorder_level >= max_stock:
        raise ValueError("Reorder level must be lower than maximum stock.")

    if initial_qty is None:
        initial_qty = max_stock

    if initial_qty < 0 or initial_qty > max_stock:
        raise ValueError("Initial quantity must be between 0 and the maximum stock.")

    medications = _load_medications()
    med_id = assign_medication_id(medications)

    medication = {
        "id": med_id,
        "name": name.title(),
        "category": category.title(),
        "description": description,
        "maxStock": int(max_stock),
        "reorderLevel": int(reorder_level),
        "currentQty": int(initial_qty),
        "updated_at": str(datetime.datetime.now()),
    }

    medications[med_id] = medication
    _save_medications(medications)
    return medication


def resupply_medication(medication_id, amount):
    medications = _load_medications()

    if medication_id not in medications:
        raise ValueError("Medication not found.")

    if amount <= 0:
        raise ValueError("Resupply amount must be greater than 0.")

    medication = medications[medication_id]
    medication["currentQty"] = min(
        medication["currentQty"] + amount,
        medication["maxStock"],
    )
    medication["updated_at"] = str(datetime.datetime.now())

    _save_medications(medications)
    return medication


def administer_medication(medication_id, patient_id, dosage):
    medications = _load_medications()
    patients = load_data("data/patients.json")

    if medication_id not in medications:
        raise ValueError("Medication not found.")

    if patient_id not in patients:
        raise ValueError("Patient not found.")

    if dosage <= 0:
        raise ValueError("Dosage must be greater than 0.")

    medication = medications[medication_id]

    if medication["currentQty"] < dosage:
        raise ValueError("Not enough stock to administer that dosage.")

    medication["currentQty"] -= dosage
    medication["updated_at"] = str(datetime.datetime.now())

    patient = patients[patient_id]
    administrations = patient.get("medications", [])
    administrations.append(
        {
            "medication_id": medication_id,
            "medication_name": medication["name"],
            "dosage": dosage,
            "administered_at": str(datetime.datetime.now()),
        }
    )
    patient["medications"] = administrations
    patient["medication"] = medication["name"]
    patient["updated_at"] = str(datetime.datetime.now())

    _save_medications(medications)
    save_data("data/patients.json", patients)
    return medication, patient
