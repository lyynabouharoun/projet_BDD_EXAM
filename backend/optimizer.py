from datetime import datetime, timedelta, time
from collections import defaultdict
import random
import math

from backend.database import (
    fetch_formations,
    fetch_modules_by_formation,
    fetch_students_by_formation,
    fetch_rooms,
    fetch_professors,
    clear_existing_exams,
    insert_exam
)
from backend.conflict_detector import is_exam_valid

# =====================================
# PARAMETERS
# =====================================
EXAM_DURATION = 90  # minutes
BREAK_DURATION = 10  # minutes
START_TIME = time(8, 0)
END_TIME = time(15, 30)
DEFAULT_GROUP_SIZE = 40

# =====================================
# HELPER FUNCTIONS
# =====================================

def generate_possible_slots(start_date, end_date):
    """Generate all valid exam slots (Mon-Wed, Sat-Sun) with 10-min breaks."""
    slots = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 3 or current.weekday() > 4:  # Mon-Wed + Sat-Sun
            slot_time = datetime.combine(current, START_TIME)
            while slot_time.time() <= END_TIME:
                slots.append(slot_time)
                slot_time += timedelta(minutes=EXAM_DURATION + BREAK_DURATION)
        current += timedelta(days=1)
    return slots

def split_students_flexible(student_ids, rooms, default_group_size=DEFAULT_GROUP_SIZE):
    """Split students into groups to fit available rooms."""
    students = list(student_ids)
    random.shuffle(students)

    rooms_sorted = sorted(rooms, key=lambda r: r["capacite"])
    groups = []
    index = 0
    for room in rooms_sorted:
        cap = min(room["capacite"], default_group_size)
        if index >= len(students):
            break
        group = set(students[index:index+cap])
        groups.append(group)
        index += cap

    while index < len(students):
        for i in range(len(groups)):
            if index >= len(students):
                break
            groups[i].add(students[index])
            index += 1

    return groups

def find_rooms_for_groups(groups, rooms, room_schedule, slot):
    """Assign rooms for each group."""
    available = [r for r in rooms if (slot.date(), slot.time()) not in room_schedule[r["salle_id"]]]
    available.sort(key=lambda r: r["capacite"])
    assignments = []

    for group in groups:
        for room in available:
            if room["capacite"] >= len(group):
                assignments.append((group, room))
                available.remove(room)
                break
        else:
            if not available:
                return None
            room = available.pop()
            group_subset = set(list(group)[:room["capacite"]])
            group_remaining = set(list(group)[room["capacite"]:])
            assignments.append((group_subset, room))
            groups.insert(0, group_remaining)
    return assignments

def pick_profs(slot, professors, prof_schedule, required=1):
    """Pick multiple professors respecting max 3 exams/day."""
    shuffled = professors[:]
    random.shuffle(shuffled)
    selected = []
    for prof in shuffled:
        exams_today = sum(1 for d, _ in prof_schedule[prof["id"]] if d == slot.date())
        if exams_today < 3:
            selected.append(prof)
        if len(selected) >= required:
            break
    if len(selected) < required:
        return None
    return selected

# =====================================
# BACKTRACKING HELPER
# =====================================

def backtrack_schedule(modules, all_student_ids, all_slots, rooms, professors,
                       prof_schedule, student_schedule, room_schedule, existing_exams):
    """Try to schedule all modules recursively (backtracking)."""
    if not modules:
        return True

    module = modules[0]

    for slot in all_slots:
        if any(slot.date() in student_schedule[sid] for sid in all_student_ids):
            continue

        groups = split_students_flexible(all_student_ids, rooms)
        room_assignments = find_rooms_for_groups(groups, rooms, room_schedule, slot)
        if not room_assignments:
            continue

        # Pick enough professors (1 per room)
        assigned_profs_list = []
        valid_exam = True
        for group, room in room_assignments:
            profs = pick_profs(slot, professors, prof_schedule, required=1)
            if not profs:
                valid_exam = False
                break

            # check conflicts
            for prof in profs:
                ok, _ = is_exam_valid(
                    existing_exams=existing_exams,
                    module_id=module["id"],
                    module_students=group,
                    salle=room,
                    prof=prof,
                    date_heure=slot,
                    duree=EXAM_DURATION,
                    module_department_id=module["departement_id"],
                    prof_list=professors
                )
                if not ok:
                    valid_exam = False
                    break
            if not valid_exam:
                break
            assigned_profs_list.append(profs)

        if not valid_exam:
            continue

        # Insert exams
        for (group, room), profs in zip(room_assignments, assigned_profs_list):
            for prof in profs:
                insert_exam(
                    module_id=module["id"],
                    salle_id=room["salle_id"],
                    prof_id=prof["id"],
                    date_exam=slot.date(),
                    heure_debut=slot.time(),
                    duree_minutes=EXAM_DURATION
                )
                existing_exams.append({
                    "module_id": module["id"],
                    "salle_id": room["salle_id"],
                    "date_heure": slot,
                    "duree_minutes": EXAM_DURATION,
                    "students": group,
                    "prof_id": prof["id"]
                })

                for sid in group:
                    student_schedule[sid].add(slot.date())
                prof_schedule[prof["id"]].add((slot.date(), slot.time()))
                room_schedule[room["salle_id"]].add((slot.date(), slot.time()))

        if backtrack_schedule(modules[1:], all_student_ids, all_slots, rooms, professors,
                              prof_schedule, student_schedule, room_schedule, existing_exams):
            return True

        # Undo if failed
        for (group, room), profs in zip(room_assignments, assigned_profs_list):
            for prof in profs:
                for sid in group:
                    student_schedule[sid].discard(slot.date())
                prof_schedule[prof["id"]].discard((slot.date(), slot.time()))
                room_schedule[room["salle_id"]].discard((slot.date(), slot.time()))
                existing_exams = [e for e in existing_exams if e["module_id"] != module["id"]]

    return False

# =====================================
# MAIN SCHEDULER
# =====================================

def generate_exam_schedule(start_date, end_date):
    print("🧠 Starting backtracking exam scheduling...")
    clear_existing_exams()

    rooms = fetch_rooms()
    formations = fetch_formations()
    professors = fetch_professors()

    prof_schedule = defaultdict(set)
    student_schedule = defaultdict(set)
    room_schedule = defaultdict(set)
    existing_exams = []

    all_slots = generate_possible_slots(start_date, end_date)
    random.shuffle(all_slots)

    for formation in formations:
        modules = fetch_modules_by_formation(formation["id"])
        students = fetch_students_by_formation(formation["id"])
        all_student_ids = {s["id"] for s in students}

        success = backtrack_schedule(
            modules, all_student_ids, all_slots, rooms, professors,
            prof_schedule, student_schedule, room_schedule, existing_exams
        )

        if not success:
            print(f"⚠️ Could not perfectly schedule formation {formation['nom']}")

    print("✅ Backtracking exam scheduling completed.")

# =====================================
# LOCAL TEST
# =====================================
if __name__ == "__main__":
    generate_exam_schedule(
        start_date=datetime(2026, 1, 6).date(),
        end_date=datetime(2026, 1, 31).date()
    )
