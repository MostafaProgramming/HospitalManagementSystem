import re


# These counters are only used if there is no saved data to inspect yet.
current_user_id = 1             
current_session_id = 1    
current_patient_id = 1     
current_medication_id = 1    
current_reminder_id = 1


def generate_prefixed_id(prefix, records=None, width=3):
    # Find the highest existing ID with the given prefix and add 1.
    if records:
        highest_value = 0
        pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")

        for key in records.keys():
            match = pattern.match(key)
            if match:
                highest_value = max(highest_value, int(match.group(1)))

        return f"{prefix}{highest_value + 1:0{width}d}"

    return None


def _assign_from_counter(prefix, counter_name, width=3):
    # Fallback used when there are no existing records yet.
    globals_dict = globals()
    identifier = f"{prefix}{globals_dict[counter_name]:0{width}d}"
    globals_dict[counter_name] += 1
    return identifier


def assign_user_id(records=None):
    # Users are stored by username, so we look inside each record for the real userID.
    if records:
        highest_value = 0
        pattern = re.compile(r"^U(\d+)$")

        for key, record in records.items():
            candidates = [key]
            if isinstance(record, dict):
                candidates.append(record.get("userID", ""))

            for candidate in candidates:
                match = pattern.match(str(candidate))
                if match:
                    highest_value = max(highest_value, int(match.group(1)))

        return f"U{highest_value + 1:03d}"

    return _assign_from_counter("U", "current_user_id")


def assign_session_id(records=None):
    generated = generate_prefixed_id("S", records)
    if generated:
        return generated
    return _assign_from_counter("S", "current_session_id")


def assign_patient_id(records=None):
    generated = generate_prefixed_id("P", records)
    if generated:
        return generated
    return _assign_from_counter("P", "current_patient_id")


def assign_medication_id(records=None):
    generated = generate_prefixed_id("M", records)
    if generated:
        return generated
    return _assign_from_counter("M", "current_medication_id")


def assign_reminder_id(records=None):
    generated = generate_prefixed_id("R", records)
    if generated:
        return generated
    return _assign_from_counter("R", "current_reminder_id")
