from datetime import timedelta


# =====================================
# TIME UTILS
# =====================================

def is_friday(date_heure):
    # Monday = 0 ... Friday = 4
    return date_heure.weekday() == 4


def overlap(start1, dur1, start2, dur2):
    end1 = start1 + timedelta(minutes=dur1)
    end2 = start2 + timedelta(minutes=dur2)
    return max(start1, start2) < min(end1, end2)


# =====================================
# CONSTRAINTS
# =====================================

def no_friday_constraint(date_heure):
    if is_friday(date_heure):
        return False, "Friday is forbidden"
    return True, None


def room_not_occupied(existing_exams, salle_id, date_heure, duree):
    for exam in existing_exams:
        if exam["salle_id"] == salle_id:
            if overlap(
                date_heure,
                duree,
                exam["date_heure"],
                exam["duree_minutes"]
            ):
                return False, "Room already used"
    return True, None


def module_only_once(existing_exams, module_id):
    for exam in existing_exams:
        if exam["module_id"] == module_id:
            return False, "Module already has an exam"
    return True, None


def students_one_exam_per_day(existing_exams, module_students, date_heure):
    exam_day = date_heure.date()

    for exam in existing_exams:
        if exam["date_heure"].date() == exam_day:
            if exam["students"].intersection(module_students):
                return False, "Student conflict same day"

    return True, None


# =====================================
# GLOBAL VALIDATION
# =====================================

def is_exam_valid(
    existing_exams,
    module_id,
    module_students,
    salle_id,
    date_heure,
    duree
):
    checks = [
        no_friday_constraint(date_heure),
        module_only_once(existing_exams, module_id),
        room_not_occupied(existing_exams, salle_id, date_heure, duree),
        students_one_exam_per_day(existing_exams, module_students, date_heure),
    ]

    for ok, reason in checks:
        if not ok:
            return False, reason

    return True, None
