# Data Sources

## Primary inspiration

Public datasets on Kaggle describing **online course enrollments** and **training completion** patterns. I used their structure (users, courses, enrollments, completions) as a blueprint.

| Reference dataset | What I borrowed |
|-------------------|-----------------|
| HR Analytics: Employee Training & Development | Program/department grouping, completion rates |
| Online Learning Platform Dataset | Course categories, enrollment timestamps |

## Synthetic data in this repo

Because Kaggle datasets cannot be redistributed in full inside a class repo, `seed/generate_lms_data.py` creates a **synthetic dataset** with similar shape:

- **120 learners** across 4 graduate programs at SJSU
- **6 online courses** (Core, Elective, Gen Ed)
- Enrollment dates, due dates, completion timestamps, and grades

All names and emails are generated with Faker (`@sjsu.edu`). No real student data is used.

## File locations

| Path | Description |
|------|-------------|
| `data/raw/` | Raw CSV exports from the generator |
| `data/processed/` | SQL query outputs + tables for Power BI |
| `data/lms.db` | SQLite warehouse (gitignored) |

## Moodle demo data

`seed/moodle_seed.php` optionally loads the same CSVs into a local Moodle Docker instance so you can compare **flat files** vs **live LMS tables**.
