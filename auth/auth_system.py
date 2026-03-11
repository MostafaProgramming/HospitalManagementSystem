import datetime
import random
import string

from auth.user import User
from auth.session import Session

from utils.hashing import hash_password
from utils.id_generator import assign_user_id, assign_session_id
from utils.json_storage import load_data, save_data

from modules.ehr import ehr_menu


# -----------------------------
# LOAD USERS FROM JSON
# -----------------------------

raw_users = load_data("data/users.json")

users_table = {}

for username, user_data in raw_users.items():

    users_table[username] = User.from_dict(user_data)


sessions = {}

current_user = None
current_session = None

Signup_key = None
session_duration_minutes = 20


# -----------------------------
# SAVE USERS FUNCTION
# -----------------------------

def save_users():

    data = {}

    for username, user_obj in users_table.items():

        data[username] = user_obj.to_dict()

    save_data("data/users.json", data)


# -----------------------------
# SIGNUP
# -----------------------------

def enteruser():

    global Signup_key

    if len(users_table) == 0:

        Signup_key = input("Create a signup key: ")
        print("\nSignup key created:", Signup_key)

    else:

        entered_key = input("Enter the signup key:")

        if entered_key != Signup_key:

            print("Invalid signup key")
            return False


    role = input("\nEnter role (Doctor, Nurse etc): ")
    username = input("Enter username: ")
    password = input("Enter password: ")

    while username in users_table:

        print("Username already exists")
        username = input("Enter another username:")

    while len(password) < 8:

        print("Password must be at least 8 characters")
        password = input("Enter password:")


    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

    password_hash = hash_password(password + salt)

    user_id = assign_user_id()

    user_obj = User(user_id, username, salt, password_hash, role)

    users_table[username] = user_obj

    save_users()

    print("\nUser created successfully")
    print("User ID:", user_id)

    return True


# -----------------------------
# LOGIN
# -----------------------------

def login():

    global current_user
    global current_session

    username = input("Enter username: ")
    password = input("Enter password: ")

    if username in users_table:

        user_obj = users_table[username]

        test_hash = hash_password(password + user_obj.salt)

        if test_hash == user_obj.password_hash:

            print("\nLogin successful")

            user_obj.last_login_at = str(datetime.datetime.now())
            user_obj.active = True

            save_users()

            current_user = user_obj

            token = assign_session_id()

            session_obj = Session(token, username, session_duration_minutes)

            sessions[token] = session_obj
            current_session = session_obj

            print("\nSession created")
            print("Session token:", session_obj.token)

            return True

        else:

            print("Incorrect password")
            return False

    else:

        print("Username not found")
        return False


# -----------------------------
# LOGOUT
# -----------------------------

def logout():

    global current_user
    global current_session

    if current_user:

        current_user.active = False

        save_users()

    if current_session:

        current_session.active = False

    current_user = None
    current_session = None

    print("\nLogged out\n")


# -----------------------------
# MAIN MENU
# -----------------------------

def main_menu():

    while True:

        print("\n--- HOSPITAL MANAGEMENT SYSTEM ---")

        print("1. EHR")
        print("2. Medication Stock")
        print("3. Staff Availability")
        print("4. Room Bookings")
        print("5. Medical Images")
        print("6. Medication Reminders")
        print("7. Logout")

        option = input("Enter choice: ")

        if option == "1":

            ehr_menu()

        elif option == "7":

            logout()
            break

        else:

            print("Feature not implemented yet")


# -----------------------------
# AUTH MENU
# -----------------------------

def auth_menu():

    while True:

        print("\n1. Login")
        print("2. Signup")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":

            if len(users_table) == 0:

                print("No users exist. Please signup first")

            else:

                success = login()

                if success:

                    main_menu()

        elif choice == "2":

            success = enteruser()

            if success:

                main_menu()

        elif choice == "3":

            break

        else:

            print("Invalid choice")