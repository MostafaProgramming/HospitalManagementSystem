from utils.json_storage import load_data, save_data
from utils.id_generator import assign_room_id, assign_booking_id
import datetime

# Load room and booking data
rooms = load_data("data/rooms.json")
bookings = load_data("data/bookings.json")


# -----------------------------
# SAVE ROOMS
# -----------------------------
def save_rooms():
    """Save room data to the JSON file"""
    save_data("data/rooms.json", rooms)


# -----------------------------
# SAVE BOOKINGS
# -----------------------------
def save_bookings():
    """Save booking data to the JSON file"""
    save_data("data/bookings.json", bookings)


# -----------------------------
# ROOM CLASS
# -----------------------------
class Room:
    def __init__(self, room_id, room_label):
        self.room_id = room_id
        self.room_label = room_label

    def to_dict(self):
        """Convert Room object to dictionary"""
        return {"room_id": self.room_id, "room_label": self.room_label}

    @staticmethod
    def from_dict(data):
        """Convert dictionary to Room object"""
        return Room(data["room_id"], data["room_label"])


# -----------------------------
# BOOKING CLASS
# -----------------------------
class Booking:
    def __init__(self, booking_id, room_id, staff_id, patient_id, start_time, end_time):
        self.booking_id = booking_id
        self.room_id = room_id
        self.staff_id = staff_id
        self.patient_id = patient_id
        self.start_time = start_time
        self.end_time = end_time

    def to_dict(self):
        """Convert Booking object to dictionary"""
        return {
            "booking_id": self.booking_id,
            "room_id": self.room_id,
            "staff_id": self.staff_id,
            "patient_id": self.patient_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    @staticmethod
    def from_dict(data):
        """Convert dictionary to Booking object"""
        return Booking(
            data["booking_id"],
            data["room_id"],
            data["staff_id"],
            data["patient_id"],
            data["start_time"],
            data["end_time"],
        )


# -----------------------------
# CHECK ROOM AVAILABILITY
# -----------------------------
def is_room_available(room_id, start_time, end_time):
    """Checks if a room is available during a specific time period"""
    for booking in bookings.values():
        if booking["room_id"] == room_id:
            # Convert string start_time and end_time from bookings to datetime
            booking_start_time = datetime.datetime.strptime(
                booking["start_time"], "%Y-%m-%d %H:%M"
            )
            booking_end_time = datetime.datetime.strptime(
                booking["end_time"], "%Y-%m-%d %H:%M"
            )

            # Check if the booking times overlap
            if start_time < booking_end_time and end_time > booking_start_time:
                return False  # Conflict found
    return True


# -----------------------------
# BOOK ROOM
# -----------------------------
def book_room(staff_id, patient_id, room_id, start_time, end_time):
    """Books a room for a patient if available"""
    if is_room_available(room_id, start_time, end_time):
        booking_id = assign_booking_id()
        new_booking = Booking(
            booking_id, room_id, staff_id, patient_id, start_time, end_time
        )
        bookings[booking_id] = new_booking.to_dict()
        save_bookings()
        print(f"Room {room_id} booked successfully! Booking ID: {booking_id}")
    else:
        print(f"Room {room_id} is not available during the selected time.")


# -----------------------------
# LIST AVAILABLE ROOMS
# -----------------------------
def list_available_rooms(start_time, end_time):
    """Lists rooms available for booking during a time window"""
    available_rooms = []
    for room in rooms.values():
        if is_room_available(room["room_id"], start_time, end_time):
            available_rooms.append(
                room["room_label"]
            )  # Return the room label for easier display
    return available_rooms


# -----------------------------
# VIEW BOOKINGS
# -----------------------------
def view_bookings_by_room(room_id):
    """View all bookings for a specific room"""
    room_bookings = []
    for booking in bookings.values():
        if booking["room_id"] == room_id:
            room_bookings.append(booking)
    return room_bookings


# -----------------------------
# CANCEL BOOKING
# -----------------------------
def cancel_booking(booking_id):
    """Cancel a booking by booking_id"""
    if booking_id in bookings:
        del bookings[booking_id]
        save_bookings()
        print(f"Booking {booking_id} cancelled.")
    else:
        print("Booking not found.")


# -----------------------------
# ROOM BOOKING MENU
# -----------------------------
def room_booking_menu():
    while True:
        print("\n---- ROOM BOOKING SYSTEM ----")
        print("1. View available rooms")
        print("2. Book room")
        print("3. View bookings by room")
        print("4. Cancel booking")
        print("5. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            # Same day check and date format input
            while True:
                start_time = input("Enter start time (YYYY-MM-DD HH:MM): ")
                end_time = input("Enter end time (YYYY-MM-DD HH:MM): ")
                try:
                    start_time = datetime.datetime.strptime(
                        start_time, "%Y-%m-%d %H:%M"
                    )
                    end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M")
                    # Ensure both times are on the same day
                    if start_time.date() != end_time.date():
                        print("Error: You can only book rooms on the same day.")
                        continue  # Re-enter start and end time
                    break
                except ValueError:
                    print("Invalid format. Please use YYYY-MM-DD HH:MM")

            available_rooms = list_available_rooms(start_time, end_time)
            print(f"Available rooms: {available_rooms}")

        elif choice == "2":
            room_id = input("Enter room ID: ")
            staff_id = input("Enter staff ID: ")
            patient_id = input("Enter patient ID: ")

            # Ensure that the user only selects a time interval on the same day
            while True:
                start_time = input("Enter start time (YYYY-MM-DD HH:MM): ")
                end_time = input("Enter end time (YYYY-MM-DD HH:MM): ")
                try:
                    start_time = datetime.datetime.strptime(
                        start_time, "%Y-%m-%d %H:%M"
                    )
                    end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M")
                    # Check that both times are on the same day
                    if start_time.date() != end_time.date():
                        print("Error: You can only book rooms on the same day.")
                        continue  # Re-enter start and end time
                    break
                except ValueError:
                    print("Invalid format. Please use YYYY-MM-DD HH:MM")

            book_room(staff_id, patient_id, room_id, start_time, end_time)

        elif choice == "3":
            room_id = input("Enter room ID: ")
            bookings_for_room = view_bookings_by_room(room_id)
            print(f"Bookings for Room {room_id}: {bookings_for_room}")

        elif choice == "4":
            booking_id = input("Enter booking ID to cancel: ")
            cancel_booking(booking_id)

        elif choice == "5":
            break

        else:
            print("Invalid choice")
