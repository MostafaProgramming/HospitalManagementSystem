import datetime

from utils.id_generator import assign_patient_id
from utils.json_storage import load_data, save_data


# -----------------------------
# LOAD PATIENT DATA
# -----------------------------

patients = load_data("data/patients.json")


# -----------------------------
# ADD PATIENT
# -----------------------------

def add_patient():

    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    phone = input("Enter phone number: ")
    dob = input("Enter date of birth: ")
    condition = input("Enter medical condition: ")
    medication = input("Enter medication: ")

    patient_id = assign_patient_id()

    patient_data = {

        "patient_id": patient_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "dob": dob,
        "condition": condition,
        "medication": medication,
        "created_at": str(datetime.datetime.now()),
        "updated_at": str(datetime.datetime.now())

    }

    patients[patient_id] = patient_data

    save_data("data/patients.json", patients)

    print("\nPatient created successfully")
    print("Patient ID:", patient_id)


# -----------------------------
# VIEW PATIENTS
# -----------------------------

def view_patients():

    if len(patients) == 0:

        print("\nNo patients found")
        return

    for patient in patients.values():

        print("\n----------------------")
        print("Patient ID:", patient["patient_id"])
        print("Name:", patient["first_name"], patient["last_name"])
        print("Email:", patient["email"])
        print("Phone:", patient["phone"])
        print("DOB:", patient["dob"])
        print("Condition:", patient["condition"])
        print("Medication:", patient["medication"])


# -----------------------------
# UPDATE PATIENT
# -----------------------------

def update_patient():

    patient_id = input("Enter patient ID to update: ")

    if patient_id not in patients:

        print("Patient not found")
        return

    patient = patients[patient_id]

    patient["first_name"] = input("Enter new first name: ")
    patient["last_name"] = input("Enter new last name: ")
    patient["email"] = input("Enter new email: ")
    patient["phone"] = input("Enter new phone: ")
    patient["condition"] = input("Enter new condition: ")
    patient["medication"] = input("Enter new medication: ")

    patient["updated_at"] = str(datetime.datetime.now())

    save_data("data/patients.json", patients)

    print("Patient updated successfully")


# -----------------------------
# DELETE PATIENT
# -----------------------------

def delete_patient():
    patient_id = input("Enter patient ID to delete: ")

    if patient_id in patients:

        del patients[patient_id]

        save_data("data/patients.json", patients)

        print("Patient deleted")

    else:

        print("Patient not found")


# -----------------------------
# EHR MENU
# -----------------------------

def ehr_menu():

    while True:

        print("\n---- EHR SYSTEM ----")

        print("1. Add patient")
        print("2. View patients")
        print("3. Update patient")
        print("4. Delete patient")
        print("5. Back")

        choice = input("Enter choice: ")

        if choice == "1":

            add_patient()

        elif choice == "2":

            view_patients()

        elif choice == "3":

            update_patient()

        elif choice == "4":

            delete_patient()

        elif choice == "5":

            break

        else:

            print("Invalid choice")