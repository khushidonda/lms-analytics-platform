#!/usr/bin/env python3
"""
Generate synthetic LMS data for the Joby Aviation Learning Analytics project.

Creates a SQLite reporting warehouse mirroring Moodle mdl_* table patterns,
exports CSVs for Power BI / Databricks, and prints a completion summary.
"""

from __future__ import annotations

import random
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "lms.db"
PROCESSED_DIR = ROOT / "data" / "processed"
RAW_DIR = ROOT / "data" / "raw"

fake = Faker()
Faker.seed(42)
random.seed(42)

DEPARTMENTS = {
    "Flight Operations": 45,
    "Engineering & Certification": 60,
    "Manufacturing & Quality": 80,
    "Safety & Compliance": 25,
    "People & HR": 20,
    "Software & Data": 35,
    "Corporate & Legal": 15,
}

COURSES = [
    {
        "shortname": "FAA-SAFETY",
        "fullname": "FAA Safety Fundamentals",
        "category": "Mandatory",
        "compliance_required": 1,
        "recert_days": 365,
        "target_departments": None,
    },
    {
        "shortname": "EMERG-PROC",
        "fullname": "Emergency Procedures Training",
        "category": "Mandatory",
        "compliance_required": 1,
        "recert_days": 180,
        "target_departments": None,
    },
    {
        "shortname": "DATA-PRIV",
        "fullname": "Data Privacy & Cybersecurity",
        "category": "Mandatory",
        "compliance_required": 1,
        "recert_days": 365,
        "target_departments": None,
    },
    {
        "shortname": "HARASS-PREV",
        "fullname": "Harassment Prevention",
        "category": "Mandatory",
        "compliance_required": 1,
        "recert_days": 365,
        "target_departments": None,
    },
    {
        "shortname": "LMS-ORIENT",
        "fullname": "LMS Platform Orientation",
        "category": "Onboarding",
        "compliance_required": 1,
        "recert_days": None,
        "target_departments": None,
    },
    {
        "shortname": "TECH-WRITE",
        "fullname": "Technical Writing & Documentation",
        "category": "Elective",
        "compliance_required": 0,
        "recert_days": None,
        "target_departments": None,
    },
    {
        "shortname": "PBI-OPS",
        "fullname": "Power BI for Operations",
        "category": "Elective",
        "compliance_required": 0,
        "recert_days": None,
        "target_departments": None,
    },
    {
        "shortname": "QMS-MFG",
        "fullname": "Quality Management Systems",
        "category": "Mandatory",
        "compliance_required": 1,
        "recert_days": 365,
        "target_departments": ["Manufacturing & Quality"],
    },
    {
        "shortname": "AVI-REG",
        "fullname": "Aviation Regulations Overview",
        "category": "Mandatory",
        "compliance_required": 1,
        "recert_days": 365,
        "target_departments": ["Flight Operations"],
    },
]

INTAKE_TYPES = [
    "New Course Request",
    "Enrollment Exception",
    "Access Issue",
    "Completion Override",
    "Report Request",
]
INTAKE_STATUSES = ["Open", "In Progress", "Resolved", "Closed"]


def to_unix(dt: datetime) -> int:
    return int(dt.timestamp())


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP TABLE IF EXISTS mdl_intake_requests;
        DROP TABLE IF EXISTS mdl_grade_grades;
        DROP TABLE IF EXISTS mdl_course_completions;
        DROP TABLE IF EXISTS mdl_user_enrolments;
        DROP TABLE IF EXISTS mdl_enrol;
        DROP TABLE IF EXISTS mdl_course;
        DROP TABLE IF EXISTS mdl_user;

        CREATE TABLE mdl_user (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL,
            hire_date TEXT NOT NULL,
            deleted INTEGER DEFAULT 0
        );

        CREATE TABLE mdl_course (
            id INTEGER PRIMARY KEY,
            shortname TEXT NOT NULL,
            fullname TEXT NOT NULL,
            category TEXT NOT NULL,
            compliance_required INTEGER NOT NULL,
            recert_days INTEGER
        );

        CREATE TABLE mdl_enrol (
            id INTEGER PRIMARY KEY,
            courseid INTEGER NOT NULL,
            enrol TEXT NOT NULL,
            status INTEGER NOT NULL
        );

        CREATE TABLE mdl_user_enrolments (
            id INTEGER PRIMARY KEY,
            enrolid INTEGER NOT NULL,
            userid INTEGER NOT NULL,
            status INTEGER NOT NULL,
            timestart INTEGER NOT NULL,
            timeend INTEGER,
            due_date TEXT
        );

        CREATE TABLE mdl_course_completions (
            id INTEGER PRIMARY KEY,
            userid INTEGER NOT NULL,
            course INTEGER NOT NULL,
            timeenrolled INTEGER NOT NULL,
            timecompleted INTEGER
        );

        CREATE TABLE mdl_grade_grades (
            id INTEGER PRIMARY KEY,
            userid INTEGER NOT NULL,
            courseid INTEGER NOT NULL,
            finalgrade REAL,
            timemodified INTEGER
        );

        CREATE TABLE mdl_intake_requests (
            id INTEGER PRIMARY KEY,
            request_type TEXT NOT NULL,
            requester_name TEXT NOT NULL,
            requester_email TEXT NOT NULL,
            department TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            created_date TEXT NOT NULL,
            resolved_date TEXT,
            assigned_to TEXT
        );
        """
    )


def generate_users() -> list[dict]:
    users = []
    user_id = 1
    for department, count in DEPARTMENTS.items():
        for _ in range(count):
            first = fake.first_name()
            last = fake.last_name()
            hire_date = fake.date_between(start_date="-3y", end_date="-14d")
            users.append(
                {
                    "id": user_id,
                    "username": f"{first.lower()}.{last.lower()}{user_id}",
                    "firstname": first,
                    "lastname": last,
                    "email": f"{first.lower()}.{last.lower()}@joby.training",
                    "department": department,
                    "role": random.choice(["Employee", "Manager", "Technician", "Analyst"]),
                    "hire_date": hire_date.isoformat(),
                    "deleted": 0,
                }
            )
            user_id += 1
    return users


def course_applies_to_user(course: dict, user: dict) -> bool:
    targets = course["target_departments"]
    if not targets:
        return True
    return user["department"] in targets


def pick_completion_status(course: dict, hire_date: date, today: date) -> str:
    tenure_days = (today - hire_date).days
    category = course["category"]

    if category == "Onboarding":
        if tenure_days <= 30:
            return random.choices(
                ["completed_on_time", "in_progress", "not_started"],
                weights=[0.55, 0.30, 0.15],
            )[0]
        return random.choices(
            ["completed_on_time", "overdue", "not_started"],
            weights=[0.95, 0.03, 0.02],
        )[0]

    if category == "Mandatory":
        return random.choices(
            ["completed_on_time", "overdue", "not_started", "in_progress"],
            weights=[0.78, 0.12, 0.06, 0.04],
        )[0]

    return random.choices(
        ["completed_on_time", "in_progress", "not_started"],
        weights=[0.45, 0.25, 0.30],
    )[0]


def build_enrollment_records(users: list[dict], courses: list[dict], today: date) -> tuple[list, list, list, list]:
    enrolments_meta = []
    user_enrolments = []
    completions = []
    grades = []

    enrol_id = 1
    enrolment_id = 1
    completion_id = 1
    grade_id = 1

    for course_idx, course in enumerate(courses, start=1):
        enrolments_meta.append(
            {
                "id": enrol_id,
                "courseid": course_idx,
                "enrol": "manual",
                "status": 0,
            }
        )

        for user in users:
            if not course_applies_to_user(course, user):
                continue

            hire_date = date.fromisoformat(user["hire_date"])
            if random.random() < 0.08 and course["category"] == "Elective":
                continue

            enrolled_dt = fake.date_time_between(
                start_date=max(hire_date, today - timedelta(days=400)),
                end_date=today - timedelta(days=7),
            )
            due_days = course["recert_days"] or 30
            due_date = (enrolled_dt.date() + timedelta(days=due_days)).isoformat()

            status = pick_completion_status(course, hire_date, today)
            completed_dt = None
            grade = None

            if status == "completed_on_time":
                completed_dt = enrolled_dt + timedelta(days=random.randint(3, max(4, due_days - 5)))
                grade = round(random.uniform(78, 100), 1)
            elif status == "overdue":
                completed_dt = None
            elif status == "in_progress":
                completed_dt = None
                grade = None
            else:
                completed_dt = None

            user_enrolments.append(
                {
                    "id": enrolment_id,
                    "enrolid": enrol_id,
                    "userid": user["id"],
                    "status": 0,
                    "timestart": to_unix(enrolled_dt),
                    "timeend": None,
                    "due_date": due_date,
                }
            )

            completions.append(
                {
                    "id": completion_id,
                    "userid": user["id"],
                    "course": course_idx,
                    "timeenrolled": to_unix(enrolled_dt),
                    "timecompleted": to_unix(completed_dt) if completed_dt else None,
                }
            )

            if grade is not None:
                grades.append(
                    {
                        "id": grade_id,
                        "userid": user["id"],
                        "courseid": course_idx,
                        "finalgrade": grade,
                        "timemodified": to_unix(completed_dt),
                    }
                )
                grade_id += 1

            enrolment_id += 1
            completion_id += 1

        enrol_id += 1

    return enrolments_meta, user_enrolments, completions, grades


def generate_intake_requests(users: list[dict], today: date) -> list[dict]:
    requests = []
    for i in range(1, 41):
        requester = random.choice(users)
        created = fake.date_between(start_date=today - timedelta(days=120), end_date=today - timedelta(days=1))
        status = random.choices(INTAKE_STATUSES, weights=[0.15, 0.20, 0.45, 0.20])[0]
        resolved = None
        if status in {"Resolved", "Closed"}:
            resolved = (created + timedelta(days=random.randint(1, 14))).isoformat()

        requests.append(
            {
                "id": i,
                "request_type": random.choice(INTAKE_TYPES),
                "requester_name": f"{requester['firstname']} {requester['lastname']}",
                "requester_email": requester["email"],
                "department": requester["department"],
                "description": fake.sentence(nb_words=12),
                "status": status,
                "created_date": created.isoformat(),
                "resolved_date": resolved,
                "assigned_to": random.choice(["Learning Tech Team", "LMS Admin", "HR Partner"]),
            }
        )
    return requests


def insert_records(conn: sqlite3.Connection, table: str, records: list[dict]) -> None:
    if not records:
        return
    columns = records[0].keys()
    placeholders = ", ".join("?" for _ in columns)
    col_names = ", ".join(columns)
    conn.executemany(
        f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})",
        [tuple(record[c] for c in columns) for record in records],
    )


def export_csv(conn: sqlite3.Connection) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    tables = [
        "mdl_user",
        "mdl_course",
        "mdl_enrol",
        "mdl_user_enrolments",
        "mdl_course_completions",
        "mdl_grade_grades",
        "mdl_intake_requests",
    ]
    for table in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        df.to_csv(PROCESSED_DIR / f"{table}.csv", index=False)
        df.to_csv(RAW_DIR / f"{table}.csv", index=False)


def print_summary(conn: sqlite3.Connection) -> None:
    summary_sql = """
    SELECT
        u.department,
        c.fullname AS course_name,
        COUNT(*) AS total_enrolled,
        SUM(CASE WHEN cc.timecompleted IS NOT NULL THEN 1 ELSE 0 END) AS total_completed,
        ROUND(100.0 * SUM(CASE WHEN cc.timecompleted IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS completion_rate_pct
    FROM mdl_user u
    JOIN mdl_course_completions cc ON cc.userid = u.id
    JOIN mdl_course c ON c.id = cc.course
    WHERE u.deleted = 0
    GROUP BY u.department, c.fullname
    ORDER BY u.department, c.fullname;
    """
    df = pd.read_sql_query(summary_sql, conn)
    print("\n=== Completion Summary by Department & Course ===")
    print(df.to_string(index=False))

    overdue_sql = """
    SELECT COUNT(*) AS overdue_count
    FROM mdl_user_enrolments ue
    JOIN mdl_enrol e ON e.id = ue.enrolid
    JOIN mdl_course_completions cc ON cc.userid = ue.userid AND cc.course = e.courseid
    WHERE ue.due_date < date('now')
      AND (cc.timecompleted IS NULL);
    """
    overdue = pd.read_sql_query(overdue_sql, conn).iloc[0]["overdue_count"]
    print(f"\nOverdue enrollments: {overdue}")


def main() -> None:
    today = date.today()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    users = generate_users()
    courses = [{**course, "id": idx} for idx, course in enumerate(COURSES, start=1)]
    course_rows = [
        {
            "id": c["id"],
            "shortname": c["shortname"],
            "fullname": c["fullname"],
            "category": c["category"],
            "compliance_required": c["compliance_required"],
            "recert_days": c["recert_days"],
        }
        for c in courses
    ]

    conn = sqlite3.connect(DB_PATH)
    try:
        create_schema(conn)
        insert_records(conn, "mdl_user", users)
        insert_records(conn, "mdl_course", course_rows)

        enrol_meta, user_enrolments, completions, grades = build_enrollment_records(users, courses, today)
        insert_records(conn, "mdl_enrol", enrol_meta)
        insert_records(conn, "mdl_user_enrolments", user_enrolments)
        insert_records(conn, "mdl_course_completions", completions)
        insert_records(conn, "mdl_grade_grades", grades)
        insert_records(conn, "mdl_intake_requests", generate_intake_requests(users, today))
        conn.commit()

        export_csv(conn)
        print_summary(conn)
        print(f"\nDatabase written to: {DB_PATH}")
        print(f"CSV exports written to: {PROCESSED_DIR}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
