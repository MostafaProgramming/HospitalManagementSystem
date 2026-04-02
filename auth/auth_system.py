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


# This function reads all saved users from the JSON file.
def _load_users():
    return load_data("data/users.json")


# This function saves the changed users back to the JSON file.
def _save_users(users):
    save_data("data/users.json", users)


# This function reads the system settings such as the signup key.
def _load_config():
    return load_data("data/config.json")

# This function saves the changed settings back to the JSON file.
def _save_config(config):
    save_data("data/config.json", config)

# This function matches the usernames without caring about upper/lower case characters.
def _find_username(users, username):
    lowered = username.strip().lower()
    for existing_username in users:
        if existing_username.lower() == lowered:
            return existing_username
    return None


def _match_password(user, password):
    stored_hash = user.get("password_hash", "")
    salt = user.get("salt", "")

    # Try the entered password first, then a trimmed version to be more forgiving
    # of accidental spaces typed into the GUI field.
    candidates = [password]
    trimmed_password = password.strip()
    if trimmed_password != password:
        candidates.append(trimmed_password)

    for candidate in candidates:
        if salt and hash_password(candidate + salt) == stored_hash:
            return candidate, False

        # Support older unsalted hashes and migrate them on the next successful login.
        if hash_password(candidate) == stored_hash:
            return candidate, True

    return None, False

# This function tells us whether this is the first account in the system.
def has_users():
    return len(_load_users()) > 0


# This function returns all of the users in alphabetical order for staff dropdowns and selections.
def list_users():
    users = _load_users()
    return sorted(users.values(), key=lambda user: user["username"].lower())


# This function creates a new staff account after checking and ensuring that the input is valid.
def register_user(role, username, password, signup_key=None):
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
        created_key = config.get("signup_key", "").strip()
        if not created_key:
            raise ValueError("No signup key is created.")
        if signup_key != created_key:
            raise ValueError("The signup key is incorrect.")
    else:
        if not signup_key:
            raise ValueError("The first user must create a signup key.")
        config["signup_key"] = signup_key
        _save_config(config)

    # This adds a random salt to the password before hashing it.
    salt = "".join(random.choices(string.ascii_letters + string.digits, k=8))
    user_id = assign_user_id(users)

    # This saves the user with the hashed password and salt, so the real password is never stored.
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


# This function checks login details and marks the matched user as the active session.
def authenticate_user(username, password):
    global current_session
    global current_user

    users = _load_users()
    matched_username = _find_username(users, username)

    if not matched_username:
        raise ValueError("Username not found.")

    user = users[matched_username]
    matched_password, needs_upgrade = _match_password(user, password)

    if matched_password is None:
        raise ValueError("Incorrect password.")

    if needs_upgrade:
        salt = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        user["salt"] = salt
        user["password_hash"] = hash_password(matched_password + salt)

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
