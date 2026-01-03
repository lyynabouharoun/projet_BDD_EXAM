from datetime import datetime, timedelta, time

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
# PARAMETERS (easy to change)
# =====================================

EXAM_DURATION = 90  # minutes

TIME_SLOTS = [
    time(8, 30),
    time(10, 30),
    time(13, 30)
]

START_DATE = datetime(2026, 1, 6)   # example
END_DATE   = datetime(2026, 1, 21)

# =====================================
# DATE GENERATOR (Mon–Thu)
# =====================================

def generate_possible_dates(start, end):
    dates = []
    current = start
    while current <= end:
        if current.weekday() < 4:  # Mon(0) → Thu(3)
            dates.append(current.date())
        current += timedelta(days=1)
    return dates

# =====================================
# MAIN OPTIMIZER
# =====================================

def generate_exam_schedule():
    print("🧠 Starting exam scheduling...")

    # Clear existing exams in DB
    clear_existing_exams()

    # Fetch data
    rooms = fetch_rooms()
    formations = fetch_formations()
    professors = fetch_professors()

    # Track professor schedules to avoid conflicts
    prof_schedule = {prof["id"]: set() for prof in professors}

    possible_dates = generate_possible_dates(START_DATE, END_DATE)

    existing_exams = []  # in-memory exams

    for formation in formations:
        print(f"📚 Formation: {formation['nom']}")

        modules = fetch_modules_by_formation(formation["id"])
        students = fetch_students_by_formation(formation["id"])
        student_ids = {s["id"] for s in students}

        for module in modules:
            print(f"  📝 Scheduling module: {module['nom']}")
            scheduled = False

            # Try all dates and time slots
            for exam_date in possible_dates:
                for slot in TIME_SLOTS:
                    date_heure = datetime.combine(exam_date, slot)

                    for room in rooms:
                        # Check constraints
                        valid, reason = is_exam_valid(
                            existing_exams=existing_exams,
                            module_id=module["id"],
                            module_students=student_ids,
                            salle_id=room["id"],
                            date_heure=date_heure,
                            duree=EXAM_DURATION
                        )

                        if not valid:
                            continue

                        # Find an available professor
                        available_prof = None
                        for prof_id in prof_schedule:
                            if (date_heure.date(), date_heure.time()) not in prof_schedule[prof_id]:
                                available_prof = prof_id
                                break

                        if available_prof is None:
                            # No professor free at this slot, try next
                            continue

                        # Insert exam into DB
                        insert_exam(
                            module_id=module["id"],
                            prof_id=available_prof,
                            salle_id=room["id"],
                            date_exam=date_heure.date(),
                            heure_debut=date_heure.time(),
                            duree=EXAM_DURATION
                        )

                        # Save in-memory for constraint checking
                        existing_exams.append({
                            "module_id": module["id"],
                            "salle_id": room["id"],
                            "date_heure": date_heure,
                            "duree_minutes": EXAM_DURATION,
                            "students": student_ids,
                            "prof_id": available_prof
                        })

                        # Mark professor busy
                        prof_schedule[available_prof].add((date_heure.date(), date_heure.time()))

                        print(f"    ✅ {exam_date} {slot} | Salle {room['nom']} | Prof ID {available_prof}")
                        scheduled = True
                        break  # room assigned, move to next module

                    if scheduled:
                        break
                if scheduled:
                    break

            if not scheduled:
                print(f"    ❌ FAILED to schedule module {module['nom']}")

    print("✅ Exam scheduling completed.")

# Optional: run directly
if __name__ == "__main__":
    generate_exam_schedule()
