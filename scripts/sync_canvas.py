"""Build or update the Strategy Leadership Lab Canvas course (37924, STRAT 490R-002).

Upserts by name, so rerunning updates in place and never touches grades. Per-student due
dates (presidency Monday tier, discussant sessions) come from
_private/canvas-overrides.json, which names students and stays out of git.

    python3 scripts/sync_canvas.py --dry-run
    python3 scripts/sync_canvas.py
"""
import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, os.path.expanduser("~/.claude/skills/canvas-lms/scripts"))
from canvas_client import CanvasAPI, load_config  # noqa: E402
from canvas_due import due, local  # noqa: E402

COURSE_ID = int(os.getenv("CANVAS_COURSE_ID", "37924"))
SITE = "https://byu-strategy.github.io/strategy-leadership-lab"
OVERRIDES = HERE.parent / "_private" / "canvas-overrides.json"

GROUPS = [
    ("Weekly update emails", 50),
    ("Attendance", 25),
    ("Feedback conversation", 10),
    ("Discussant", 15),
]

# Fridays with class. No class Oct 16 or Nov 27 (discussant sign-up sheet, 2026-10-05).
SESSIONS = ["2026-09-04", "2026-09-11", "2026-09-18", "2026-09-25", "2026-10-02",
            "2026-10-09", "2026-10-23", "2026-10-30", "2026-11-06", "2026-11-13",
            "2026-11-20", "2026-12-04"]
# Weeks with an update: every Friday Sep 11 to Dec 4 except Thanksgiving week.
UPDATE_FRIDAYS = ["2026-09-11", "2026-09-18", "2026-09-25", "2026-10-02", "2026-10-09",
                  "2026-10-16", "2026-10-23", "2026-10-30", "2026-11-06", "2026-11-13",
                  "2026-11-20", "2026-12-04"]


def short(d):
    return date.fromisoformat(d).strftime("%b %-d")


def plus(d, days):
    return (date.fromisoformat(d) + timedelta(days=days)).isoformat()


UPDATE_DESC = f"""<p>Send your weekly update email to the person you report to, with
<strong>strategy-program@byu.edu</strong> in CC. The CC is how completion is tracked; an update
without it does not count. Nothing is submitted in Canvas.</p>
<table border="1" cellpadding="6" style="border-collapse: collapse;">
<tr><th>You are</th><th>Full credit</th><th>Half credit through</th><th>No credit</th></tr>
<tr><td>VPs</td><td>Fri, 11:59 PM</td><td>Mon, 11:59 PM</td><td>After Monday</td></tr>
<tr><td>Presidencies</td><td>Mon, 11:59 PM</td><td>Wed, 11:59 PM</td><td>After Wednesday</td></tr>
</table>
<p>Format, who sends to whom, and an example: <a href="{SITE}/03-weekly-updates.html">Weekly Updates</a>.</p>"""

ATTEND_DESC = f"""<p>Attendance for this session. Nothing to submit. Everyone gets one free
absence: the first session you miss still earns credit. See
<a href="{SITE}/00-assessments.html#attendance">Attendance</a>.</p>"""

REFLECTION_DESC = f"""<p>Hold one 30 minute feedback conversation with the person you report to
between Nov 17 and Dec 4, then submit this reflection. It is graded on completion. Nothing
anyone says about you affects your grade.</p>
<ol>
<li>Who you met with and when</li>
<li>The one thing you are working on next</li>
<li>One thing you committed to as a result</li>
<li>One thing you asked them to do differently</li>
</ol>
<p>Write about yourself, not about them. See
<a href="{SITE}/04-peer-feedback.html">Feedback Conversations</a>.</p>"""

DISCUSSANT_DESC = f"""<p>Once during the semester, with up to two classmates, pick a company or
leader, email a short pre-read to the class and link it in the sign-up sheet by Tuesday
11:59 PM, and lead a 15 minute discussion that Friday. Nothing is submitted in Canvas. Your due
date is your session. See <a href="{SITE}/05-discussant.html">Being a Discussant</a>.</p>"""

DISCUSSANT_RUBRIC = [
    ("Pre-read emailed to the class and linked in the sign-up sheet on time", 5),
    ("You brought questions for the class", 5),
    ("The class discussed; you did not present", 5),
]


def build_assignments(ov):
    """Every assignment: name -> dict(group, points, due, desc, types, overrides, position)."""
    pres = list(ov["presidency_monday_tier"])
    out = []
    for i, fri in enumerate(UPDATE_FRIDAYS, 1):
        out.append(dict(name=f"Weekly Update {i}: week of {short(fri)}", group="Weekly update emails",
                        points=1, due=due(fri), desc=UPDATE_DESC, types=["none"],
                        overrides=[dict(title="Presidencies (Monday)", student_ids=pres,
                                        due_at=due(plus(fri, 3)))]))
    for i, d in enumerate(SESSIONS, 1):
        out.append(dict(name=f"Attendance {i}: {short(d)}", group="Attendance", points=1,
                        due=due(f"{d} 13:45"), desc=ATTEND_DESC, types=["none"], overrides=[]))
    out.append(dict(name="Feedback Conversation Reflection", group="Feedback conversation",
                    points=10, due=due("2026-12-04"), desc=REFLECTION_DESC,
                    types=["online_text_entry"], overrides=[]))
    disc_ov = [dict(title=f"Discussants {short(d)}", student_ids=list(ids), due_at=due(f"{d} 12:30"))
               for d, ids in sorted(ov["discussant_sessions"].items())]
    out.append(dict(name="Discussant", group="Discussant", points=15, due=None,
                    desc=DISCUSSANT_DESC, types=["none"], overrides=disc_ov))
    return out


def modules_plan(by_name):
    """[(module name, [assignment names])], one module per Friday."""
    plan = []
    fridays = sorted(set(SESSIONS) | set(UPDATE_FRIDAYS))
    for f in fridays:
        items = [n for n in by_name if n.endswith(f": {short(f)}") and n.startswith("Attendance")]
        items += [n for n in by_name if n.endswith(f"week of {short(f)}")]
        if f == "2026-12-04":
            items.append("Feedback Conversation Reflection")
        label = f"Fri, {short(f)}" + ("" if f in SESSIONS else " (no class)")
        plan.append((label, items))
    return plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    api = CanvasAPI(cfg["url"], cfg["token"], COURSE_ID)
    ov = json.loads(OVERRIDES.read_text())
    enrolled = {str(e["user_id"]) for e in api.get_all("/enrollments", params={"type[]": "StudentEnrollment"})}
    for ids in [ov["presidency_monday_tier"], *ov["discussant_sessions"].values()]:
        missing = set(ids) - enrolled
        if missing:
            sys.exit(f"Not enrolled in {COURSE_ID}: {sorted(missing)}")

    assignments = build_assignments(ov)
    if args.dry_run:
        for a in assignments:
            d = local(a["due"]) if a["due"] else "no base due date"
            print(f"{a['group']:<22} {a['name']:<40} {a['points']:>3} pts  {d}")
            for o in a["overrides"]:
                print(f"{'':<22}   override {o['title']} ({len(o['student_ids'])}): {local(o['due_at'])}")
        print(f"\n{len(assignments)} assignments")
        for m, items in modules_plan([a["name"] for a in assignments]):
            print(f"module {m}: {items}")
        return

    # Groups: reuse the default empty "Assignments" group as the first one.
    groups = {g["name"]: g for g in api.get_all("/assignment_groups")}
    if "Assignments" in groups and GROUPS[0][0] not in groups:
        g = groups.pop("Assignments")
        api.put(f"/assignment_groups/{g['id']}", json={"name": GROUPS[0][0]})
        groups[GROUPS[0][0]] = g
    gid = {}
    for pos, (name, weight) in enumerate(GROUPS, 1):
        if name in groups:
            api.put(f"/assignment_groups/{groups[name]['id']}", json={"group_weight": weight, "position": pos})
            gid[name] = groups[name]["id"]
        else:
            gid[name] = api.post("/assignment_groups", json={"name": name, "group_weight": weight, "position": pos})["id"]
    api.put("", json={"course": {"apply_assignment_group_weights": True}})

    existing = {a["name"]: a for a in api.get_all("/assignments")}
    ids = {}
    for pos, a in enumerate(assignments, 1):
        body = {"assignment": {"name": a["name"], "points_possible": a["points"], "due_at": a["due"],
                               "assignment_group_id": gid[a["group"]], "description": a["desc"],
                               "submission_types": a["types"], "grading_type": "points",
                               "published": True}}
        if a["name"] in existing:
            aid = existing[a["name"]]["id"]
            api.put(f"/assignments/{aid}", json=body)
            state = "updated"
        else:
            aid = api.post("/assignments", json=body)["id"]
            state = "created"
        ids[a["name"]] = aid
        # Overrides hold no grades, so replace them wholesale.
        for o in api.get_all(f"/assignments/{aid}/overrides"):
            api.delete(f"/assignments/{aid}/overrides/{o['id']}")
        for o in a["overrides"]:
            api.post(f"/assignments/{aid}/overrides", json={"assignment_override": o})
        print(f"{state:<8} {a['name']}")

    # Discussant rubric, once.
    disc = api.get(f"/assignments/{ids['Discussant']}")
    if not disc.get("rubric"):
        crit = {str(i): {"description": d, "points": p,
                         "ratings": {"0": {"description": "Met", "points": p},
                                     "1": {"description": "Not met", "points": 0}}}
                for i, (d, p) in enumerate(DISCUSSANT_RUBRIC)}
        api.post("/rubrics", json={
            "rubric": {"title": "Discussant", "points_possible": 15, "criteria": crit},
            "rubric_association": {"association_id": ids["Discussant"], "association_type": "Assignment",
                                   "use_for_grading": True, "purpose": "grading"}})
        print("created  Discussant rubric")

    # Modules: organizational only, safe to rebuild.
    api.clear_modules()
    start = api.create_module("Start here", 1)
    api.add_module_url(start["id"], "Course website: syllabus, schedule, assessments", SITE + "/", 1)
    api.add_module_url(start["id"], "Discussant sign-up sheet",
                       ov["signup_sheet_url"], 2)
    api.add_module_assignment(start["id"], ids["Discussant"], 3)
    api.publish_module(start["id"])
    for pos, (label, items) in enumerate(modules_plan(list(ids)), 2):
        m = api.create_module(label, pos)
        for j, n in enumerate(items, 1):
            api.add_module_assignment(m["id"], ids[n], j)
        api.publish_module(m["id"])
    print("rebuilt  modules")


if __name__ == "__main__":
    main()
