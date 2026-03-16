current_user_id = 1
current_session_id = 1
current_patient_id = 1
current_medication_id = 1


def assign_user_id():
    global current_user_id
    user_id = "U00" + str(current_user_id)
    current_user_id += 1
    return user_id


def assign_session_id():
    global current_session_id
    session_id = "S00" + str(current_session_id)
    current_session_id += 1
    return session_id


def assign_patient_id():
    global current_patient_id
    patient_id = "P00" + str(current_patient_id)
    current_patient_id += 1
    return patient_id

#def assign_medication_id():
#    global current_medication_id
#    medication_id = "M00" + str(current_medication_id)
#    current_medication_id += 1
#    return medication_id

def assign_medication_id():
    global current_medication_id
    med_id = "M" + str(current_medication_id).zfill(3)
    current_medication_id += 1
    return med_id