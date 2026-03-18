import datetime

from utils.id_generator import assign_patient_id            # This imports the function to assign a unique patient ID
from utils.json_storage import load_data, save_data
import utils.id_generator as id_gen


# This loads the patients from the JSON file
patients = load_data("data/patients.json")

# Set the ID counter based on existing data so new entries don't overwrite old ones
if patients:
    existing_nums = [int(k[3:]) for k in patients.keys() if k.startswith("P00")]
    if existing_nums:
        id_gen.current_patient_id = max(existing_nums) + 1      



# This function adds a new patient to the patients dictionary
def add_patient():

    # This gets the patient details from the user
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    phone = input("Enter phone number: ")
    dob = input("Enter date of birth: ")
    condition = input("Enter medical condition: ")
    medication = input("Enter medication: ")

    # This assigns a unique patient ID
    patient_id = assign_patient_id()

    # 29 - 43 = These lines create a dictionary with the patient details
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

    # This saves the updated patients dictionary to the JSON file.
    save_data("data/patients.json", patients)

    # This prints a success message with the patient ID.
    print("\nPatient created successfully")
    print("Patient ID:", patient_id)



# This function displays all patients in the patients dictionary.
def view_patients():

    if len(patients) == 0:

        print("\nNo patients found")
        return

    # This iterates through the patients dictionary and prints the details of each patient.
    for patient in patients.values():

        print("\n----------------------")
        print("Patient ID:", patient["patient_id"])
        print("Name:", patient["first_name"], patient["last_name"])
        print("Email:", patient["email"])
        print("Phone:", patient["phone"])
        print("DOB:", patient["dob"])
        print("Condition:", patient["condition"])
        print("Medication:", patient["medication"])


# This function lets the user update a patient's details.
def update_patient():

    patient_id = input("Enter patient ID to update: ")

    # This checks if the patient ID exists in the patients dictionary.
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


# This function deletes a patient from the patients dictionary.
def delete_patient():

    patient_id = input("Enter patient ID to delete: ")

    if patient_id in patients:

        del patients[patient_id]

        save_data("data/patients.json", patients)

        print("Patient deleted")

    else:

        print("Patient not found")

# This function displays the EHR menu and lets the users choose the following options.
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