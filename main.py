import hashlib
import datetime
import random
import string

users_table = {}
run = True
current_user_id = 1
current_user = None

class user:
    def __init__(self, userID, username, salt, password_hash):
        self.userID = userID
        self.username = username
        #self.password = password
        self.salt = salt
        self.password_hash = password_hash
        #self.created_at = created_at
        #self.last_login_at = last_login_at
        #self.active = active

def hash_password(password):
     encoded_password = password.encode('utf-8')  # Convert the password to bytes
     hash = hashlib.sha256(encoded_password)
     hash = hash.hexdigest()
     return hash

def assign_user_id():
     global current_user_id
     user_id = str("U00")+ str(current_user_id)
     current_user_id += 1
     return user_id

def enteruser():
    username = str(input("Enter username: "))
    password = str(input("Enter password: "))
    while len(password) < 8:
        print("Password must be at least 8 characters long")
        password = str(input("Enter password: "))
        
    
    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    password = str(password) + str(salt[0]) + str(salt[1]) + str(salt[2])  + str(salt[3])  + str(salt[4])
    password_hash = hash_password(password)
    user_id = assign_user_id()
    
    User = user(user_id ,username, salt, password_hash)
    users_table[username] = User
    
    print(f"User ID: {user_id}\n")
    print(f"Username: {username}\n")
    print(f"Password: {password}\n")
    print(f"Salt: {salt}\n")
    print(f"Password Hash: {password_hash}\n")


def user_creation():
      global run
      while run:
          enteruser()
          print("User created successfully")
          choice = input("Do you want to create another user? (y/n): ")
          while choice != "y" and choice != "n":
              print("Invalid choice\n")
              choice = input("Do you want to create another user? (y/n): ")
          if choice == "n":
              run = False
user_creation()

def login():
    global current_user
    
    username = input("Enter username: ")
    password = input("Enter password: ")

    if username in users_table:
        user_obj = users_table[username]
        
        test_hash = hash_password(password + user_obj.salt)

        if test_hash == user_obj.password_hash:
            print("Login successful")
            current_user = user_obj
            print("Users Table:\n")
            print(users_table)
            return True

        else:
            print("Incorrect password")
            return False
    else:
        print("User not found")
        return False

choice = input("1 = Login, 2 = Create User: ")
if choice == "1":
    login()
elif choice == "2":
    user_creation()


