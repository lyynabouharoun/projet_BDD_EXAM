from datetime import timedelta, datetime

# =====================================
# TIME UTILITIES
# =====================================

def is_friday(date_heure):
    """Friday is the only day off."""
    return date_heure.weekday() == 4  # Monday=0 ... Friday=4

def next_valid_day(date_heure):
    """
    Returns the next valid exam day according to constraints.
    Friday is skipped.
    """
    next_day = date_heure + timedelta(days=1)
    while is_friday(next_day):
        next_day += timedelta(days=1)
    return next_day

def overlap(start1, dur1, start2, dur2):
    """
    Checks if two time intervals overlap.
    """
    end1 = start1 + timedelta(minutes=dur1)
    end2 = start2 + timedelta(minutes=dur2)
    return max(start1, start2) < min(end1, end2)

# =====================================
# CONSTRAINT CHECKERS
# =====================================

def no_friday_constraint(date_heure):
    if is_friday(date_heure):
        return False, "Exams cannot be scheduled on Friday"
    return True, None

def room_capacity_constraint(salle, module_students_count):
    """
    Check if room can hold all students
    """
    if salle["capacite"] < module_students_count:
        return False, "Room capacity exceeded"
    return True, None

def room_not_occupied(existing_exams, salle_id, date_heure, duree):
    for exam in existing_exams:
        if exam["salle_id"] != salle_id:
            continue
        existing_start = exam["date_heure"]   # <-- use "date_heure"
        existing_end = existing_start + timedelta(minutes=exam["duree_minutes"])
        new_start = date_heure
        new_end = date_heure + timedelta(minutes=duree)
        if max(existing_start, new_start) < min(existing_end, new_end):
            return False, f"Salle {salle_id} is occupied"
    return True, None

def module_only_once(existing_exams, module_id):
    for exam in existing_exams:
        if exam["module_id"] == module_id:
            return False, "This module already has an exam scheduled"
    return True, None

def students_one_exam_per_day(existing_exams, module_students, date_heure):
    """
    Checks if any student has more than 1 exam per day
    """
    exam_day = date_heure.date()
    for exam in existing_exams:
        if exam["date_heure"].date() == exam_day:
            if set(exam["students"]).intersection(module_students):
                return False, "Student conflict: multiple exams in same day"
    return True, None

def professors_max_three_per_day(existing_exams, prof_id, date_heure):
    """
    Check if professor has exceeded 3 exams in one day
    """
    exam_day = date_heure.date()
    count = 0
    for exam in existing_exams:
        if exam["prof_id"] == prof_id and exam["date_heure"].date() == exam_day:
            count += 1
    if count >= 3:
        return False, f"Professor {prof_id} already has 3 exams scheduled that day"
    return True, None

def professors_department_priority(prof, module_department_id):
    """
    Optional: ensure professors supervise exams in their department first
    """
    if prof["departement_id"] != module_department_id:
        return False, "Professor should prioritize exams in their own department"
    return True, None

def equal_distribution_of_surveillance(existing_exams, prof_list):
    """
    Ensure all professors have roughly equal number of exams assigned
    """
    prof_count = {p["id"]: 0 for p in prof_list}
    for exam in existing_exams:
        prof_count[exam["prof_id"]] += 1
    max_count = max(prof_count.values())
    min_count = min(prof_count.values())
    if max_count - min_count > 1:
        return False, "Professor exam load is unbalanced"
    return True, None

# =====================================
# GLOBAL EXAM VALIDATION
# =====================================

def is_exam_valid(existing_exams, module_id, module_students,
                  salle, prof, date_heure, duree, module_department_id,
                  prof_list):
    """
    Checks all constraints for a proposed exam
    """
    checks = [
        no_friday_constraint(date_heure),
        module_only_once(existing_exams, module_id),
        room_not_occupied(existing_exams, salle["salle_id"], date_heure, duree),
        students_one_exam_per_day(existing_exams, module_students, date_heure),
        professors_max_three_per_day(existing_exams, prof["id"], date_heure),
        room_capacity_constraint(salle, len(module_students)),
        professors_department_priority(prof, module_department_id),
        equal_distribution_of_surveillance(existing_exams, prof_list)
    ]

    for ok, reason in checks:
        if not ok:
            return False, reason
    return True, None
