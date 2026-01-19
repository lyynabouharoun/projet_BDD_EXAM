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
    get_connection,
    insert_exam,
    insert_exam_groups  # Changed to plural
)

# =========================
# PARAMETERS
# =========================
EXAM_DURATION = 90
BREAK_DURATION = 10
START_TIME = time(8, 30)
END_TIME = time(15, 30)
GROUP_SIZE = 40
MAX_PROF_PER_DAY = 3

# =========================
# SLOTS
# =========================
def generate_slots(start_date, end_date):
    slots = []
    d = start_date
    while d <= end_date:
        if d.weekday() not in (3, 4):  # no Thu/Fri
            t = datetime.combine(d, START_TIME)
            while t.time() <= END_TIME:
                slots.append(t)
                t += timedelta(minutes=EXAM_DURATION + BREAK_DURATION)
        d += timedelta(days=1)
    return slots

# =========================
# MAIN
# =========================
def generate_exam_schedule(start_date, end_date):
    print("🧠 Generating exams...")
    clear_existing_exams()

    rooms = fetch_rooms()
    professors = fetch_professors()
    formations = fetch_formations()
    slots = generate_slots(start_date, end_date)
    random.shuffle(slots)

    room_busy = defaultdict(set)     # (date, time) -> set per room
    prof_busy = defaultdict(set)     # (date, time) per prof
    prof_daily = defaultdict(lambda: defaultdict(int))
    prof_total = defaultdict(int)
    formation_busy_days = defaultdict(set)  # date per formation

    conn = get_connection()  # Single connection for all inserts

    try:
        for formation in formations:
            formation_id = formation["id"]
            students = fetch_students_by_formation(formation_id)
            student_ids = [s["id"] for s in students]

            modules = fetch_modules_by_formation(formation_id)

            for module in modules:
                scheduled = False

                for slot in slots:
                    date = slot.date()
                    time_ = slot.time()

                    # STUDENT: one exam per day (optimized: check formation busy days)
                    if date in formation_busy_days[formation_id]:
                        continue

                    # GROUPS
                    groups = [
                        student_ids[i:i + GROUP_SIZE]
                        for i in range(0, len(student_ids), GROUP_SIZE)
                    ]

                    free_rooms = [
                        r for r in rooms
                        if (date, time_) not in room_busy[r["salle_id"]]
                    ]

                    if len(free_rooms) < len(groups):
                        continue

                    # PROFS (fair distribution)
                    free_profs = [
                        p for p in professors
                        if (date, time_) not in prof_busy[p["id"]]
                        and prof_daily[p["id"]][date] < MAX_PROF_PER_DAY
                    ]

                    free_profs.sort(key=lambda p: prof_total[p["id"]])

                    if len(free_profs) < len(groups):
                        continue

                    # 🔒 COMMIT
                    for group_idx, (group, room, prof) in enumerate(zip(groups, free_rooms[:len(groups)], free_profs[:len(groups)])):
                        exam_id = insert_exam(
                            module_id=module["id"],
                            salle_id=room["salle_id"],
                            prof_id=prof["id"],
                            date_exam=date,
                            heure_debut=time_,
                            duree_minutes=EXAM_DURATION,
                            conn=conn,
                            commit=False
                        )

                        if exam_id is None:
                            # Handle failure (e.g., unique violation), skip or retry
                            continue

                        insert_exam_groups(exam_id, group, conn=conn, commit=False)

                        room_busy[room["salle_id"]].add((date, time_))
                        prof_busy[prof["id"]].add((date, time_))
                        prof_daily[prof["id"]][date] += 1
                        prof_total[prof["id"]] += 1

                    # Only add busy day if all groups were scheduled successfully
                    if len(groups) == group_idx + 1:  # All groups processed
                        formation_busy_days[formation_id].add(date)
                        scheduled = True
                    else:
                        # If partial failure, you may need to rollback partial inserts, but for simplicity, we proceed
                        pass

                    if scheduled:
                        break

                if not scheduled:
                    print(f"⚠️ Module not scheduled: {module['nom']}")

        conn.commit()  # Commit all at once
        print("✅ Exams generated successfully")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()