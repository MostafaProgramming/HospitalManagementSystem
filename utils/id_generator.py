current_user_id = 1
current_session_id = 1
current_patient_id = 1
current_medication_id = 1
current_room_id = 1
current_booking_id = 1


def assign_user_id():
    global current_user_id
    user_id = "U" + str(current_user_id).zfill(3)
    current_user_id += 1
    return user_id


def assign_session_id():
    global current_session_id
    session_id = "S" + str(current_session_id).zfill(3)
    current_session_id += 1
    return session_id


def assign_patient_id():
    global current_patient_id
    patient_id = "P" + str(current_patient_id).zfill(3)
    current_patient_id += 1
    return patient_id


def assign_medication_id():
    global current_medication_id
    medication_id = "M" + str(current_medication_id).zfill(3)
    current_medication_id += 1
    return medication_id

def assign_room_id():
    global current_room_id
    room_id = "R" + str(current_room_id).zfill(3)
    current_room_id += 1
    return room_id

def assign_booking_id():
    global current_booking_id
    booking_id = "B" + str(current_booking_id).zfill(3)
    current_booking_id += 1
    return booking_id