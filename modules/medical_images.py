import datetime
from pathlib import Path

from utils.id_generator import assign_image_id
from utils.json_storage import load_data, save_data


DATE_FORMAT = "%Y-%m-%d"


def _load_images():
    return load_data("data/medical_images.json")


def _save_images(images):
    save_data("data/medical_images.json", images)


def list_medical_images():
    images = _load_images()
    return sorted(images.values(), key=lambda image: (image["patient_id"], image["captured_on"]))


def get_medical_image(image_id):
    images = _load_images()

    if image_id not in images:
        raise ValueError("Medical image not found.")

    return images[image_id]


def add_medical_image(patient_id, image_type, body_part, captured_on, file_path, uploaded_by, notes=""):
    patients = load_data("data/patients.json")
    images = _load_images()

    if patient_id not in patients:
        raise ValueError("Patient not found.")

    if not image_type.strip():
        raise ValueError("Image type is required.")

    try:
        datetime.datetime.strptime(captured_on.strip(), DATE_FORMAT)
    except ValueError as exc:
        raise ValueError("Captured date must use YYYY-MM-DD.") from exc

    normalised_path = str(Path(file_path).expanduser()) if file_path.strip() else ""

    image_id = assign_image_id(images)
    image = {
        "image_id": image_id,
        "patient_id": patient_id,
        "image_type": image_type.strip().title(),
        "body_part": body_part.strip().title(),
        "captured_on": captured_on.strip(),
        "file_path": normalised_path,
        "uploaded_by": uploaded_by.strip(),
        "notes": notes.strip(),
    }

    images[image_id] = image
    _save_images(images)
    return image


def delete_medical_image(image_id):
    images = _load_images()

    if image_id not in images:
        raise ValueError("Medical image not found.")

    image = images.pop(image_id)
    _save_images(images)
    return image
