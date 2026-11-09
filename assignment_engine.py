# assignment_engine.py
import random as rnd
import models


def normalize_language(lang):
    if not lang:
        return None
    mapping = {
        'ingilizce': 'English', 'english': 'English',
        'almanca': 'German', 'german': 'German',
        'türkçe': 'Turkish', 'turkce': 'Turkish', 'turkish': 'Turkish',
        'fransızca': 'French', 'fransizca': 'French', 'french': 'French',
        'ispanyolca': 'Spanish', 'i̇spanyolca': 'Spanish', 'spanish': 'Spanish',
    }
    key = lang.strip().lower().replace('\u0307', '')
    return mapping.get(key, lang.strip())


def assign_students_random(students, classrooms):
    if not classrooms:
        return {}, list(students)
    students = list(students)
    rnd.shuffle(students)
    total = len(students)
    n = len(classrooms)
    base = total // n
    extra = total % n
    sorted_rooms = sorted(classrooms, key=lambda c: c.capacity, reverse=True)
    assignments = {}
    remaining = list(students)
    extra_left = extra
    for room in sorted_rooms:
        if not remaining:
            break
        target = base + (1 if extra_left > 0 else 0)
        if extra_left > 0:
            extra_left -= 1
        take = min(target, room.capacity, len(remaining))
        if take > 0:
            assigned = remaining[:take]
            remaining = remaining[take:]
            assignments[room.id] = [s.id for s in assigned]
    if remaining:
        for room in sorted_rooms:
            if not remaining:
                break
            current = len(assignments.get(room.id, []))
            space = room.capacity - current
            if space > 0:
                take = min(space, len(remaining))
                assigned = remaining[:take]
                remaining = remaining[take:]
                assignments.setdefault(room.id, []).extend([s.id for s in assigned])
    return assignments, remaining


def assign_students_grouped(students, classrooms, group_attr):
    groups = {}
    for s in students:
        key = getattr(s, group_attr, 'Unknown') or 'Unknown'
        groups.setdefault(key, []).append(s)
    buildings = {}
    for c in classrooms:
        buildings.setdefault(c.building_id, []).append(c)
    building_list = []
    for bid, rooms in buildings.items():
        total_cap = sum(c.capacity for c in rooms)
        building_list.append((bid, rooms, total_cap))
    building_list.sort(key=lambda x: -x[2])
    assignments = {}
    classroom_fill = {c.id: 0 for c in classrooms}
    remaining_students = []
    sorted_groups = sorted(groups.items(), key=lambda kv: -len(kv[1]))
    for _, group_students in sorted_groups:
        group_queue = list(group_students)
        for bid, rooms, _cap in building_list:
            if not group_queue:
                break
            remaining_cap = sum(c.capacity - classroom_fill[c.id] for c in rooms)
            if remaining_cap == 0:
                continue
            for room in rooms:
                if not group_queue:
                    break
                space = room.capacity - classroom_fill[room.id]
                if space <= 0:
                    continue
                take = min(space, len(group_queue))
                assigned = group_queue[:take]
                group_queue = group_queue[take:]
                assignments.setdefault(room.id, []).extend([s.id for s in assigned])
                classroom_fill[room.id] += take
        remaining_students.extend(group_queue)
    return assignments, remaining_students


def assign_supervisors(buildings_used, building_supervisors, proctors):
    supervisor_assignments = {}
    available = list(proctors)
    used_ids = set()
    for bid in buildings_used:
        dedicated = next((s for s in building_supervisors if s.building_id == bid), None)
        if dedicated:
            supervisor_assignments[bid] = dedicated.id
            continue
        candidates = [p for p in available
                      if p.preferred_building_id == bid
                      and p.can_be_supervisor
                      and p.id not in used_ids]
        if candidates:
            chosen = candidates[0]
            supervisor_assignments[bid] = chosen.id
            used_ids.add(chosen.id)
            available = [p for p in available if p.id != chosen.id]
    return supervisor_assignments, available


def pick_best_proctor(candidates, classroom, language):
    if not candidates:
        return None
    scored = []
    for p in candidates:
        score = 0
        if language and language in p.languages:
            score += 10
        if p.preferred_building_id == classroom.building_id:
            score += 5
        score += rnd.random() * 0.01
        scored.append((score, p))
    scored.sort(key=lambda x: -x[0])
    return scored[0][1]


def _expand_exam_into_groups(exam, students):
    """Returns a list of group dicts: {'exam', 'language', 'students'}"""
    exam_students = [s for s in students if s.exam_id == exam.id]
    if not exam_students:
        return []
    if getattr(exam, 'split_by_language', False):
        by_lang = {}
        for s in exam_students:
            lang = normalize_language(s.language) or exam.language or 'Unknown'
            by_lang.setdefault(lang, []).append(s)
        return [{'exam': exam, 'language': lang, 'students': studs}
                for lang, studs in by_lang.items()]
    else:
        return [{'exam': exam, 'language': exam.language, 'students': exam_students}]


def generate_session_assignments(session_exams, students, classrooms, proctors, building_supervisors):
    all_groups = []
    for e in session_exams:
        all_groups.extend(_expand_exam_into_groups(e, students))

    if not all_groups:
        return [], "No students for any exam in this session", 0
    for e in session_exams:
        if e.proctors_per_classroom_default < 1:
            return [], f"Invalid proctor count for exam {e.name}", 0
    if not classrooms:
        return [], "No classrooms available", 0
    if not proctors:
        return [], "No proctors available", 0

    all_groups.sort(key=lambda g: -len(g['students']))

    regular = [c for c in classrooms if not c.is_reserve]
    reserve = [c for c in classrooms if c.is_reserve]

    available_rooms = sorted(regular, key=lambda c: c.capacity, reverse=True)
    for g in all_groups:
        needed = len(g['students'])
        chosen = []
        cap = 0
        while cap < needed and available_rooms:
            r = available_rooms.pop(0)
            chosen.append(r)
            cap += r.capacity
        g['rooms'] = chosen

    student_assignments = {}
    classroom_language = {}
    classroom_exam = {}
    overflow = []

    for g in all_groups:
        rooms = g['rooms']
        studs = g['students']
        exam = g['exam']
        lang = g['language']

        if not rooms:
            overflow.extend(studs)
            continue

        if exam.distribution_strategy == 'same_department':
            sub, leftover = assign_students_grouped(studs, rooms, 'department')
        elif exam.distribution_strategy == 'same_faculty':
            sub, leftover = assign_students_grouped(studs, rooms, 'faculty')
        else:
            sub, leftover = assign_students_random(studs, rooms)

        for cid, sids in sub.items():
            student_assignments.setdefault(cid, []).extend(sids)
            classroom_language[cid] = lang
            classroom_exam[cid] = exam
        if leftover:
            overflow.extend(leftover)

    if overflow:
        reserve_sub, leftover = assign_students_random(overflow, reserve)
        for cid, sids in reserve_sub.items():
            student_assignments.setdefault(cid, []).extend(sids)
            first_s = next((s for s in students if s.id == sids[0]), None)
            if first_s:
                classroom_language[cid] = normalize_language(first_s.language) or 'Unknown'
            classroom_exam[cid] = session_exams[0]
        if leftover:
            return [], f"Not enough capacity! {len(leftover)} students unassigned", 0

    used_cids = set(student_assignments.keys())
    for c in reserve:
        used_cids.add(c.id)

    buildings_used = set()
    for cid in used_cids:
        c = next((c for c in classrooms if c.id == cid), None)
        if c:
            buildings_used.add(c.building_id)

    supervisor_map, proctors_after_promo = assign_supervisors(
        buildings_used, building_supervisors, proctors
    )

    regular_proctors = [p for p in proctors_after_promo if not p.is_reserve]
    reserve_proctors = [p for p in proctors_after_promo if p.is_reserve]

    regular_used = [cid for cid in used_cids
                    if not next((c for c in classrooms if c.id == cid and c.is_reserve), None)]
    reserve_used = [cid for cid in used_cids
                    if next((c for c in classrooms if c.id == cid and c.is_reserve), None)]

    def get_required(cid):
        exam = classroom_exam.get(cid)
        if exam is None:
            return 1
        return exam.proctors_per_classroom_default

    proctor_map = {}
    available = list(regular_proctors)
    sorted_regular = sorted(regular_used, key=lambda cid: -len(student_assignments.get(cid, [])))

    for cid in sorted_regular:
        if not available:
            break
        room = next((c for c in classrooms if c.id == cid), None)
        if not room:
            continue
        lang = classroom_language.get(cid)
        best = pick_best_proctor(available, room, lang)
        if best:
            proctor_map.setdefault(cid, []).append(best.id)
            available = [p for p in available if p.id != best.id]

    max_req = max((get_required(cid) for cid in regular_used), default=0)
    for _ in range(1, max_req):
        for cid in sorted_regular:
            if not available:
                break
            if len(proctor_map.get(cid, [])) >= get_required(cid):
                continue
            room = next((c for c in classrooms if c.id == cid), None)
            if not room:
                continue
            lang = classroom_language.get(cid)
            best = pick_best_proctor(available, room, lang)
            if best:
                proctor_map.setdefault(cid, []).append(best.id)
                available = [p for p in available if p.id != best.id]

    if reserve_used:
        pool = reserve_proctors + available
        for cid in reserve_used:
            if not pool:
                break
            room = next((c for c in classrooms if c.id == cid), None)
            if not room:
                continue
            lang = classroom_language.get(cid)
            best = pick_best_proctor(pool, room, lang)
            if best:
                proctor_map.setdefault(cid, []).append(best.id)
                pool = [p for p in pool if p.id != best.id]

    assignments = []
    for cid in used_cids:
        c = next((c for c in classrooms if c.id == cid), None)
        if not c:
            continue
        owning_exam = classroom_exam.get(cid) or session_exams[0]
        assignments.append(models.Assignment(
            id=0,
            exam_id=owning_exam.id,
            classroom_id=cid,
            proctor_ids=proctor_map.get(cid, []),
            student_ids=student_assignments.get(cid, []),
            is_reserve=c.is_reserve,
            building_supervisor_id=supervisor_map.get(c.building_id),
        ))

    total = sum(len(g['students']) for g in all_groups)
    total_needed = sum(get_required(cid) for cid in regular_used)
    total_assigned = sum(len(v) for v in proctor_map.values())
    if total_assigned < total_needed:
        short = total_needed - total_assigned
        return assignments, f"OK (warning: {short} proctor slots unfilled)", total

    return assignments, "OK", total


def generate_assignments(exam, students, classrooms, proctors, building_supervisors):
    return generate_session_assignments([exam], students, classrooms, proctors, building_supervisors)