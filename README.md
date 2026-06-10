# LMS Analytics & Reporting Platform

**Khushi Donda** | Interview prep for Joby Aviation — Learning Systems & Analytics Intern

A full-stack learning analytics platform simulating enterprise LMS operations at an aviation company. Includes a live Moodle instance (Docker), a SQL reporting warehouse, compliance dashboards, SOP documentation, and intake request management.

---

## What This Project Demonstrates

| Joby JD Requirement | How This Project Covers It |
|---------------------|---------------------------|
| LMS administration, enrollments, course setup | Moodle Docker + admin SOPs |
| SQL data extraction & validation | 5 production SQL queries with CTEs & window functions |
| Learning reports & dashboards | Power BI 5-page dashboard (setup guide included) |
| SOP documentation & data lineage | 4 SOPs + `DATA_LINEAGE.md` |
| Moodle / Totara experience | Moodle 4.3 running locally |
| Databricks analytics | PySpark notebook included |
| Intake request management | `mdl_intake_requests` table + SOP-004 |

---

## Tech Stack

- **LMS:** Moodle (Docker — `erseco/alpine-moodle` + MariaDB 11)
- **Database:** SQLite reporting warehouse (mirrors Moodle `mdl_*` schema)
- **Data Generation:** Python 3.11, Faker, Pandas
- **Analytics:** SQL (CTEs, window functions), Power BI, Databricks
- **Documentation:** Markdown SOPs, data lineage, course catalog

---

## Quick Start

### 1. Generate the dataset

```bash
cd lms-analytics-platform
python3 -m venv .venv
source .venv/bin/activate
pip install -r seed/requirements.txt
python seed/generate_lms_data.py
python seed/run_sql_exports.py
```

### 2. Run Moodle locally (optional — for LMS admin practice)

```bash
docker compose up -d
# Moodle: http://localhost:8080  (admin / Admin123!)
# MySQL:  localhost:3306         (moodle / moodle)
```

### 3. Build the Power BI dashboard

Follow step-by-step instructions in [`powerbi/POWERBI_SETUP.md`](powerbi/POWERBI_SETUP.md).

### 4. Explore SQL queries

```bash
sqlite3 data/lms.db < sql/02_overdue_compliance.sql
```

---

## Dataset Overview

| Entity | Count |
|--------|-------|
| Employees | 280 across 7 departments |
| Courses | 9 (mandatory, elective, onboarding) |
| Enrollments | ~2,400 |
| Intake Requests | 40 |
| Overdue Records | ~289 (by design) |

**Departments:** Flight Operations, Engineering & Certification, Manufacturing & Quality, Safety & Compliance, People & HR, Software & Data, Corporate & Legal

---

## Project Structure

```
lms-analytics-platform/
├── docker-compose.yml          # Moodle + MariaDB
├── seed/
│   ├── generate_lms_data.py    # Synthetic data generator
│   ├── run_sql_exports.py      # Export query results to CSV
│   └── requirements.txt
├── sql/
│   ├── 01_enrollment_summary.sql
│   ├── 02_overdue_compliance.sql
│   ├── 03_participation_trend.sql
│   ├── 04_data_validation.sql
│   └── 05_compliance_score.sql
├── data/
│   ├── processed/              # CSV exports for Power BI
│   └── lms.db                  # SQLite warehouse (generated)
├── powerbi/
│   └── POWERBI_SETUP.md        # Dashboard build guide + DAX
├── databricks/
│   └── lms_compliance_analysis.py
└── docs/
    ├── DATA_LINEAGE.md
    ├── COURSE_CATALOG.md
    └── sops/                   # SOP-001 through SOP-004
```

---

## Key SQL Example — Overdue Compliance

```sql
SELECT u.department, c.fullname, COUNT(*) AS overdue_count
FROM mdl_user u
JOIN mdl_user_enrolments ue ON ue.userid = u.id
JOIN mdl_enrol e ON e.id = ue.enrolid
JOIN mdl_course c ON c.id = e.courseid
LEFT JOIN mdl_course_completions cc
    ON cc.userid = u.id AND cc.course = c.id
WHERE c.compliance_required = 1
  AND ue.due_date < date('now')
  AND cc.timecompleted IS NULL
GROUP BY u.department, c.fullname;
```

---

## Interview Talking Points

1. **Why Moodle?** Listed in the Joby JD as a desired platform; running it locally gave real admin experience with course setup, enrollments, and completion tracking.
2. **Hardest part?** Moodle only records completions when a course is finished — identifying "not started" users required `LEFT JOIN` + `NULL` checks.
3. **Documentation?** Three operational SOPs plus data lineage so any team member can trace every dashboard metric to its source table.
4. **Aviation context?** Departments and courses mirror FAA certification training needs at a company like Joby.

---

## Author

**Khushi Donda** — MS Applied Data Intelligence, San Jose State University  
[GitHub](https://github.com/khushidonda) | khushidonda.work@gmail.com
