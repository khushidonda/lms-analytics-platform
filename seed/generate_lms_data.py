#!/usr/bin/env python3
"""
Generate synthetic online-learning data for the SJSU Data Visualization course project.

Inspired by public "employee training / online learning platform" datasets on Kaggle.
Creates a SQLite warehouse (Moodle-style table names), CSV exports for Power BI,
and optional seeding into the local Moodle demo.
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

INSTITUTION = "San Jose State University"
EMAIL_DOMAIN = "sjsu.edu"

# Medium-sized dataset: 4 graduate programs × ~30 students
PROGRAMS = {
    "MS Business Analytics": 32,
    "MS Data Science": 30,
    "MS Information Systems": 28,
    "MS Applied Data Intelligence": 30,
}

COURSES = [
    {
        "shortname": "DATA-VIZ-101",
        "fullname": "Introduction to Data Visualization",
        "category": "Core",
        "is_core_course": 1,
        "term_days": 90,
        "target_programs": None,
    },
    {
        "shortname": "BUS-STAT-200",
        "fullname": "Business Statistics",
        "category": "Core",
        "is_core_course": 1,
        "term_days": 90,
        "target_programs": ["MS Business Analytics", "MS Applied Data Intelligence"],
    },
    {
        "shortname": "PY-ANALYTICS",
        "fullname": "Python for Data Analysis",
        "category": "Core",
        "is_core_course": 1,
        "term_days": 90,
        "target_programs": ["MS Data Science", "MS Applied Data Intelligence"],
    },
    {
        "shortname": "RES-METHODS",
        "fullname": "Research Methods",
        "category": "Core",
        "is_core_course": 1,
        "term_days": 90,
        "target_programs": None,
    },
    {
        "shortname": "INFO-SYS-100",
        "fullname": "Information Systems Fundamentals",
        "category": "Elective",
        "is_core_course": 0,
        "term_days": 60,
        "target_programs": ["MS Information Systems"],
    },
    {
        "shortname": "ACAD-WRITE",
        "fullname": "Academic Writing & Communication",
        "category": "Gen Ed",
        "is_core_course": 0,
        "term_days": 45,
        "target_programs": None,
    },
]


def to_unix(dt: datetime) -> int:
    return int(dt.timestamp())


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
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
            program TEXT NOT NULL,
            student_level TEXT NOT NULL,
            cohort_start TEXT NOT NULL,
            deleted INTEGER DEFAULT 0
        );

        CREATE TABLE mdl_course (
            id INTEGER PRIMARY KEY,
            shortname TEXT NOT NULL,
            fullname TEXT NOT NULL,
            category TEXT NOT NULL,
            is_core_course INTEGER NOT NULL,
            term_days INTEGER
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
        """
    )


def generate_users() -> list[dict]:
    users = []
    user_id = 1
    for program, count in PROGRAMS.items():
        for _ in range(count):
            first = fake.first_name()
            last = fake.last_name()
            cohort_start = fake.date_between(start_date="-2y", end_date="-30d")
            users.append(
                {
                    "id": user_id,
                    "username": f"{first.lower()}.{last.lower()}{user_id}",
                    "firstname": first,
                    "lastname": last,
                    "email": f"{first.lower()}.{last.lower()}@{EMAIL_DOMAIN}",
                    "program": program,
                    "student_level": random.choice(
                        ["Graduate Student", "Graduate Student", "Teaching Assistant"]
                    ),
                    "cohort_start": cohort_start.isoformat(),
                    "deleted": 0,
                }
            )
            user_id += 1
    return users


def course_applies_to_user(course: dict, user: dict) -> bool:
    targets = course["target_programs"]
    if not targets:
        return True
    return user["program"] in targets


def pick_completion_status(course: dict, cohort_start: date, today: date) -> str:
    weeks_enrolled = (today - cohort_start).days / 7
    category = course["category"]

    if category == "Gen Ed":
        return random.choices(
            ["completed_on_time", "in_progress", "not_started"],
            weights=[0.70, 0.20, 0.10],
        )[0]

    if category == "Core":
        if weeks_enrolled < 4:
            return random.choices(
                ["completed_on_time", "in_progress", "not_started"],
                weights=[0.35, 0.40, 0.25],
            )[0]
        return random.choices(
            ["completed_on_time", "past_due", "not_started", "in_progress"],
            weights=[0.72, 0.10, 0.08, 0.10],
        )[0]

    return random.choices(
        ["completed_on_time", "in_progress", "not_started"],
        weights=[0.50, 0.28, 0.22],
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
            {"id": enrol_id, "courseid": course_idx, "enrol": "manual", "status": 0}
        )

        for user in users:
            if not course_applies_to_user(course, user):
                continue

            if random.random() < 0.12 and course["category"] == "Elective":
                continue

            cohort_start = date.fromisoformat(user["cohort_start"])
            enrolled_dt = fake.date_time_between(
                start_date=max(cohort_start, today - timedelta(days=300)),
                end_date=today - timedelta(days=5),
            )
            due_days = course["term_days"]
            due_date = (enrolled_dt.date() + timedelta(days=due_days)).isoformat()

            status = pick_completion_status(course, cohort_start, today)
            completed_dt = None
            grade = None

            if status == "completed_on_time":
                completed_dt = enrolled_dt + timedelta(days=random.randint(7, max(8, due_days - 3)))
                grade = round(random.uniform(72, 98), 1)
            elif status == "past_due":
                completed_dt = None
            elif status == "in_progress":
                grade = round(random.uniform(60, 85), 1) if random.random() < 0.3 else None

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
                        "timemodified": to_unix(completed_dt) if completed_dt else to_unix(enrolled_dt),
                    }
                )
                grade_id += 1

            enrolment_id += 1
            completion_id += 1

        enrol_id += 1

    return enrolments_meta, user_enrolments, completions, grades


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
    ]
    for table in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        df.to_csv(PROCESSED_DIR / f"{table}.csv", index=False)
        df.to_csv(RAW_DIR / f"{table}.csv", index=False)


def print_summary(conn: sqlite3.Connection) -> None:
    summary_sql = """
    SELECT
        u.program,
        c.fullname AS course_name,
        COUNT(*) AS total_enrolled,
        SUM(CASE WHEN cc.timecompleted IS NOT NULL THEN 1 ELSE 0 END) AS total_completed,
        ROUND(100.0 * SUM(CASE WHEN cc.timecompleted IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS completion_rate_pct
    FROM mdl_user u
    JOIN mdl_course_completions cc ON cc.userid = u.id
    JOIN mdl_course c ON c.id = cc.course
    WHERE u.deleted = 0
    GROUP BY u.program, c.fullname
    ORDER BY u.program, c.fullname;
    """
    df = pd.read_sql_query(summary_sql, conn)
    print("\n=== Completion Summary by Program & Course ===")
    print(df.to_string(index=False))

    past_due_sql = """
    SELECT COUNT(*) AS past_due_count
    FROM mdl_user_enrolments ue
    JOIN mdl_enrol e ON e.id = ue.enrolid
    JOIN mdl_course_completions cc ON cc.userid = ue.userid AND cc.course = e.courseid
    WHERE ue.due_date < date('now') AND cc.timecompleted IS NULL;
    """
    past_due = pd.read_sql_query(past_due_sql, conn).iloc[0]["past_due_count"]
    print(f"\nPast-due enrollments: {past_due}")


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
            "is_core_course": c["is_core_course"],
            "term_days": c["term_days"],
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
        conn.commit()

        export_csv(conn)
        print_summary(conn)
        print(f"\nDatabase written to: {DB_PATH}")
        print(f"CSV exports written to: {PROCESSED_DIR}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
