import datetime
import random
import string

from auth.session import Session
from utils.hashing import hash_password
from utils.id_generator import assign_session_id, assign_user_id
from utils.json_storage import load_data, save_data


# This file handles user accounts, login, logout, and session tracking.
SESSION_DURATION_MINUTES = 20

current_user = None
current_session = None
sessions = {}


def _load_users():
    # Read all saved users from the JSON file.
    return load_data("data/users.json")


def _save_users(users):
    # Save the changed users back to the JSON file.
    save_data("data/users.json", users)


def _load_config():
    # Read system settings such as the signup key.
    return load_data("data/config.json")


def _save_config(config):
    # Save changed settings back to the JSON file.
    save_data("data/config.json", config)


def _find_username(users, username):
    # Match usernames without caring about upper/lower case.
    lowered = username.strip().lower()
    for existing_username in users:
        if existing_username.lower() == lowered:
            return existing_username
    return None


def has_users():
    # Used to tell whether this is the first account in the system.
    return len(_load_users()) > 0


def list_users():
    # Return users in alphabetical order for staff dropdowns and tables.
    users = _load_users()
    return sorted(users.values(), key=lambda user: user["username"].lower())


def register_user(role, username, password, signup_key=None):
    # Create a new staff account after checking the input is valid.
    users = _load_users()
    config = _load_config()

    role = role.strip().title()
    username = username.strip()
    signup_key = (signup_key or "").strip()

    if not role:
        raise ValueError("Role is required.")

    if not username:
        raise ValueError("Username is required.")

    if _find_username(users, username):
        raise ValueError("Username already exists.")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    if users:
        configured_key = config.get("signup_key", "").strip()
        if not configured_key:
            raise ValueError("No signup key is configured.")
        if signup_key != configured_key:
            raise ValueError("The signup key is incorrect.")
    else:
        if not signup_key:
            raise ValueError("The first user must create a signup key.")
        config["signup_key"] = signup_key
        _save_config(config)

    # A random salt is added so that matching passwords do not produce matching hashes.
    salt = "".join(random.choices(string.ascii_letters + string.digits, k=8))
    user_id = assign_user_id(users)

    users[username] = {
        "userID": user_id,
        "username": username,
        "salt": salt,
        "password_hash": hash_password(password + salt),
        "role": role,
        "created_at": str(datetime.datetime.now()),
        "last_login_at": None,
        "active": False,
    }

    _save_users(users)
    return users[username]


def authenticate_user(username, password):
    # Check login details and mark the matched user as the active session.
    global current_session
    global current_user

    users = _load_users()
    matched_username = _find_username(users, username)

    if not matched_username:
        raise ValueError("Username not found.")

    user = users[matched_username]
    # The entered password is hashed with the saved salt before comparison.
    test_hash = hash_password(password + user["salt"])

    if test_hash != user["password_hash"]:
        raise ValueError("Incorrect password.")

    for existing_username, record in users.items():
        record["active"] = existing_username == matched_username

    user["last_login_at"] = str(datetime.datetime.now())
    user["active"] = True
    _save_users(users)

    # A session token is created so the app can track the logged in user in memory.
    token = assign_session_id(sessions)
    session = Session(token, matched_username, SESSION_DURATION_MINUTES)
    sessions[token] = session

    current_session = session
    current_user = dict(user)
    return dict(user)


def logout_user():
    # Mark the user as logged out and close the in-memory session.
    global current_session
    global current_user

    if current_user:
        users = _load_users()
        username = current_user["username"]
        if username in users:
            users[username]["active"] = False
            _save_users(users)

    if current_session:
        current_session.active = False

    current_user = None
    current_session = None


def get_current_user():
    # Return a copy so the caller cannot accidentally edit the real session object.
    return dict(current_user) if current_user else None


def get_signup_key_hint():
    # The first user creates the signup key. Later users must enter it.
    if has_users():
        return "Enter the staff signup key."
    return "Create the signup key for future staff accounts."
