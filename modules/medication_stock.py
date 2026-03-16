from utils.json_storage import load_data, save_data
from utils.id_generator import assign_medication_id

# Load medications and patients from JSON files
medications = load_data("data/medications.json")
patients = load_data("data/patients.json")


class Medication:
    def __init__(self, med_id, name, category, description, max_stock, reorder_level, current_qty):
        self.id = med_id
        self.name = name
        self.category = category
        self.description = description
        self.max_stock = max_stock
        self.reorder_level = reorder_level
        self.current_qty = current_qty

    def to_dict(self):
        """ Convert the Medication object to a dictionary """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "maxStock": self.max_stock,
            "reorderLevel": self.reorder_level,
            "currentQty": self.current_qty
        }


# -----------------------------
# ADD MEDICATION
# -----------------------------

def add_medication():
    name = input("Enter medication name: ")
    category = input("Enter medication category (e.g painkiller, antibiotic): ")
    description = input("Enter medication description: ")

    # Input validation for max_stock (must be between 10 and 100)
    while True:
        try:
            max_stock = int(input("Enter maximum stock level (between 10 and 100): "))
            if 10 <= max_stock <= 100:
                break  # Exit the loop if the input is valid
            else:
                print("Please enter a value between 10 and 100.")
        except ValueError:
            print("Please enter a valid integer for maximum stock level.")

    # Input validation for reorder_level (must be between 10 and 100, and less than max_stock)
    while True:
        try:
            reorder_level = int(input("Enter reorder level (between 10 and 100): "))
            if 10 <= reorder_level <= 100:
                if reorder_level < max_stock:
                    break  # Exit the loop if the input is valid
                else:
                    print("Reorder level must be less than max stock.")
            else:
                print("Please enter a value between 10 and 100.")
        except ValueError:
            print("Please enter a valid integer for reorder level.")

    # Generate a unique medication ID
    med_id = assign_medication_id()

    # Create the Medication object
    medication = Medication(med_id, name, category, description, max_stock, reorder_level, max_stock)

    # Add medication to the medications dictionary
    medications[med_id] = medication

    # Save the updated medications dictionary to the JSON file
    save_medications()

    # Confirm medication was added
    print("Medication added successfully")
    print("Medication ID:", med_id)


# -----------------------------
# SAVE MEDICATIONS
# -----------------------------

def save_medications():
    """ Convert Medication objects to dictionaries and save to JSON """
    data = {}
    for med_id, medication in medications.items():
        data[med_id] = medication.to_dict()  # Convert to dictionary using to_dict() method
    save_data("data/medications.json", data)


# -----------------------------
# VIEW STOCK LEVELS
# -----------------------------

def view_medications():
    if len(medications) == 0:
        print("No medications registered")
        return

    for med in medications.values():
        print("\n----------------------")
        print("ID:", med.id)  # Access 'id' as a key in the medication dictionary
        print("Name:", med.name)
        print("Category:", med.category)
        print("Description:", med.description)
        print("Stock:", str(med.current_qty) + "/" + str(med.max_stock))

        # Low stock warning
        if med.current_qty < med.reorder_level:
            print("⚠ LOW STOCK")


# -----------------------------
# RESUPPLY MEDICATION
# -----------------------------

def resupply_medication():
    med_id = input("Enter medication ID: ")

    if med_id not in medications:
        print("Medication not found")
        return

    med = medications[med_id]

    # Check if the stock is already full
    if med.current_qty >= med.max_stock:
        print(f"The stock for {med.name} is already full.")
        return

    # Input validation for amount to resupply
    while True:
        try:
            amount = int(input("Enter amount to add: "))
            # Ensure the resupply amount doesn't exceed max stock
            if amount <= 0:
                print("Amount must be a positive number")
            elif amount + med.current_qty > med.max_stock:
                print(f"Cannot resupply more than {med.max_stock - med.current_qty} units. Adjusting resupply amount.")
                amount = med.max_stock - med.current_qty  # Adjust to max stock
                break
            else:
                break
        except ValueError:
            print("Please enter a valid integer for the amount.")

    # Add the resupplied amount to current stock
    med.current_qty += amount

    # Ensure current stock doesn't exceed max stock (in case of input manipulation)
    if med.current_qty > med.max_stock:
        med.current_qty = med.max_stock

    # Save the updated medications dictionary to the JSON file
    save_medications()

    # Confirm resupply
    print(f"{amount} units of {med.name} resupplied")
    print("Current stock:", med.current_qty)


# -----------------------------
# USE MEDICATION (Administer medication to a patient)
# -----------------------------

def use_medication():

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
            dosage = int(input(f"Enter dosage amount for {medications[med_id].name} (1-10): "))
            if 1 <= dosage <= 10:
                break
            else:
                print("Dosage must be between 1 and 10.")
        except ValueError:
            print("Please enter a valid integer for dosage.")

    # Check if enough stock is available for the dosage
    if medications[med_id].current_qty >= dosage:
        # Administer medication
        medications[med_id].current_qty -= dosage  # Decrease stock by the dosage given

        # Update the patient's record
        if "medications" not in patients[patient_id]:
            patients[patient_id]["medications"] = []

        patients[patient_id]["medications"].append({
            "medication_id": med_id,
            "medication_name": medications[med_id].name,
            "dosage": dosage
        })

        # Save the updated medications and patients dictionaries to JSON
        save_medications()
        save_data("data/patients.json", patients)

        print(f"{dosage} units of {medications[med_id].name} administered to patient {patient_id}.")
        print("Remaining stock:", medications[med_id].current_qty)
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