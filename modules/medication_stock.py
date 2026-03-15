from utils.json_storage import load_data, save_data
from utils.id_generator import assign_medication_id

# Load medications from JSON file
medications = load_data("data/medications.json")


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
        "currentQty": max_stock  # Initial stock equals max stock
    }

    # Add medication to the medications dictionary
    medications[med_id] = medication

    # Save the updated medications dictionary to the JSON file
    save_data("data/medications.json", medications)

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
            print("⚠ LOW STOCK")


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
    save_data("data/medications.json", medications)

    # Confirm resupply
    print(f"{amount} units of {med['name']} resupplied")
    print("Current stock:", med["currentQty"])


# -----------------------------
# USE MEDICATION
# -----------------------------

def use_medication():

    med_id = input("Enter medication ID used: ")

    if med_id not in medications:
        print("Medication not found")
        return

    med = medications[med_id]

    # Check if medication is out of stock
    if med["currentQty"] <= 0:
        print("Out of stock")
        return

    # Decrease the stock by 1 each time the medication is used
    med["currentQty"] -= 1

    # Save the updated medications dictionary to the JSON file
    save_data("data/medications.json", medications)

    # Confirm usage
    print(f"{med['name']} used. Remaining stock: {med['currentQty']}")


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