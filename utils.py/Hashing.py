import hashlib

def hash_password(password):

    encoded_password = password.encode("utf-8")

    return hashlib.sha256(encoded_password).hexdigest()