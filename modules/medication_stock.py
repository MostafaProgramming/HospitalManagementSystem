from utils.json_storage import load_data, save_data
from utils.id_generator import assign_medication_id

# Load medications from JSON file
medications = load_data("data/medications.json")


# -----------------------------
# SAVE MEDICATIONS
# -----------------------------


def save_medications():
    """Convert Medication objects to dictionaries (if needed) and save to JSON"""
    data = {}
    # Loop through all medications and convert to dictionary only if not already a dictionary
    for med_id, medication in medications.items():
        # Check if medication is a dictionary and skip to_dict() if it's already in the correct format
        if isinstance(medication, dict):
            data[med_id] = (
                medication  # Use the medication as is if it’s already a dictionary
            )
        else:
            data[med_id] = (
                medication.to_dict()
            )  # Convert to dictionary using to_dict() method
    save_data("data/medications.json", data)  # Save it without overwriting


# -----------------------------
# ADD MEDICATION
# -----------------------------


def add_medication():
    name = input("Enter medication name: ")
    category = input("Enter medication category (e.g painkiller, antibiotic): ")
    description = input("Enter medication description: ")

    # Input validation for max_stock
    while True:
        try:
            max_stock = int(input("Enter maximum stock level: "))
            break  # Exit the loop if the input is valid
        except ValueError:
            print("Please enter a valid integer for maximum stock level.")

    # Input validation for reorder_level
    while True:
        try:
            reorder_level = int(input("Enter reorder level: "))
            if reorder_level >= max_stock:
                print("Reorder level must be lower than max stock. Please try again.")
            else:
                break  # Exit the loop if the input is valid
        except ValueError:
            print("Please enter a valid integer for reorder level.")

    # Generate a unique medication ID
    med_id = assign_medication_id()

    # Create the medication object
    medication = {
        "id": med_id,
        "name": name,
        "category": category,
        "description": description,
        "maxStock": max_stock,
        "reorderLevel": reorder_level,
        "currentQty": max_stock,  # Initial stock equals max stock
    }

    # Add medication to the medications dictionary
    medications[med_id] = medication

    # Save the updated medications dictionary to the JSON file
    save_medications()

    # Confirm medication was added
    print("Medication added successfully")
    print("Medication ID:", med_id)


# -----------------------------
# VIEW STOCK LEVELS
# -----------------------------


def view_medications():
    if len(medications) == 0:
        print("No medications registered")
        return

    for med in medications.values():
        print("\n----------------------")
        print("ID:", med["id"])
        print("Name:", med["name"])
        print("Category:", med["category"])
        print("Description:", med["description"])
        print("Stock:", str(med["currentQty"]) + "/" + str(med["maxStock"]))

        # Low stock warning
        if med["currentQty"] < med["reorderLevel"]:
            print("Warning, LOW STOCK")


# -----------------------------
# RESUPPLY MEDICATION
# -----------------------------


def resupply_medication():
    med_id = input("Enter medication ID: ")

    if med_id not in medications:
        print("Medication not found")
        return

    # Input validation for amount
    while True:
        try:
            amount = int(input("Enter amount to add: "))
            if amount <= 0:
                print("Amount must be a positive number")
            else:
                break
        except ValueError:
            print("Please enter a valid integer for the amount.")

    med = medications[med_id]

    # Add the resupplied amount to current stock
    med["currentQty"] += amount

    # Ensure current stock doesn't exceed max stock
    if med["currentQty"] > med["maxStock"]:
        med["currentQty"] = med["maxStock"]

    # Save the updated medications dictionary to the JSON file
    save_medications()

    # Confirm resupply
    print(f"{amount} units of {med['name']} resupplied")
    print("Current stock:", med["currentQty"])


# -----------------------------
# USE MEDICATION
# -----------------------------


def use_medication():
    patients = load_data("data/patients.json")

    med_id = input("Enter medication ID used: ")

    if med_id not in medications:
        print("Medication not found")
        return

    # Enter patient ID
    patient_id = input("Enter patient ID: ")

    # Check if the patient ID is valid
    if patient_id not in patients:
        print("Patient not found")
        return

    # Input validation for dosage amount (between 1 and 10)
    while True:
        try:
            dosage = int(
                input(f"Enter dosage amount for {medications[med_id]['name']} (1-10): ")
            )
            if 1 <= dosage <= 10:
                break
            else:
                print("Dosage must be between 1 and 10.")
        except ValueError:
            print("Please enter a valid integer for dosage.")

    # Check if enough stock is available for the dosage
    if medications[med_id]["currentQty"] >= dosage:
        # Administer medication
        medications[med_id]["currentQty"] -= dosage

        # Update the patient's record
        if "medications" not in patients[patient_id]:
            patients[patient_id]["medications"] = []

        patients[patient_id]["medications"].append(
            {
                "medication_id": med_id,
                "medication_name": medications[med_id]["name"],
                "dosage": dosage,
            }
        )

        # Save the updated medications and patients dictionaries to JSON
        save_medications()
        save_data("data/patients.json", patients)

        print(
            f"{dosage} units of {medications[med_id]['name']} administered to patient {patient_id}."
        )
        print("Remaining stock:", medications[med_id]["currentQty"])
    else:
        print("Not enough stock to administer that dosage.")


# -----------------------------
# MEDICATION MENU
# -----------------------------


def medication_menu():
    while True:
        print("\n---- MEDICATION STOCK SYSTEM ----")

        print("1 Add medication")
        print("2 View stock levels")
        print("3 Resupply medication")
        print("4 Use medication")
        print("5 Back")

        choice = input("Enter choice: ")

        if choice == "1":
            add_medication()

        elif choice == "2":
            view_medications()

        elif choice == "3":
            resupply_medication()

        elif choice == "4":
            use_medication()

        elif choice == "5":
            break

        else:
            print("Invalid choice")
