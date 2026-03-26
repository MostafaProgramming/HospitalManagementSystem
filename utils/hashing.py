import hashlib


# Passwords are turned into a hash before storage.
# This means the app does not keep plain text passwords in the data file.
def hash_password(password):
    encoded_password = password.encode("utf-8")
    return hashlib.sha256(encoded_password).hexdigest()
