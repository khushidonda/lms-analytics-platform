# LMS Analytics & Reporting Platform

**Khushi Donda** | MS Applied Data Intelligence — San Jose State University

A college capstone-style project that simulates enterprise Learning Management System (LMS) operations and learning analytics. Includes Moodle (Docker), a SQL reporting warehouse, Power BI dashboards, SOP documentation, and intake request tracking.

---

## What This Project Demonstrates

| Skill Area | Implementation |
|------------|----------------|
| LMS administration | Moodle Docker setup, course creation, user enrollment |
| SQL analytics | 5 queries with CTEs and window functions |
| BI dashboards | Power BI 5-page dashboard (setup guide included) |
| Documentation | 4 SOPs + data lineage mapping |
| Data engineering | Python data generation, CSV/SQLite warehouse |
| Databricks | PySpark compliance notebook |

---

## Tech Stack

- **LMS:** Moodle (Docker — `erseco/alpine-moodle`)
- **Database:** MariaDB (Moodle) + SQLite (reporting warehouse)
- **Data Generation:** Python 3, Faker, Pandas
- **Analytics:** SQL, Power BI, Databricks
- **Documentation:** Markdown SOPs

---

## Quick Start

### 1. Generate analytics data

```bash
cd lms-analytics-platform
python3 -m venv .venv && source .venv/bin/activate
pip install -r seed/requirements.txt
python seed/generate_lms_data.py
python seed/run_sql_exports.py
```

### 2. Start Moodle

```bash
docker compose up -d
# Wait 2–3 minutes on first run
# http://localhost:8080 — admin / Admin123!
```

### 3. Feed data into Moodle

```bash
chmod +x seed/seed_moodle.sh
./seed/seed_moodle.sh
```

This loads **280 students**, **9 courses**, enrollments, and completion records into the live Moodle UI.

### 4. Build Power BI dashboard

Follow [`powerbi/POWERBI_SETUP.md`](powerbi/POWERBI_SETUP.md).

---

## Dataset Overview

| Entity | Count |
|--------|-------|
| Students / employees | 280 across 7 departments |
| Courses | 9 (mandatory, elective, onboarding) |
| Enrollments | ~2,000+ |
| Intake requests | 40 |

**Departments:** Computer Science, Business Analytics, Information Systems, Data Science, Engineering, Health Sciences, Liberal Arts

**Student login:** any username from `data/processed/mdl_user.csv` / password `Student123!`

---

## Project Structure

```
lms-analytics-platform/
├── seed/
│   ├── generate_lms_data.py    # Analytics warehouse + CSV exports
│   ├── moodle_seed.php         # Loads data into live Moodle
│   └── seed_moodle.sh          # One-command Moodle seeding
├── sql/                        # 5 analytics queries
├── data/processed/             # CSVs for Power BI + Moodle seed
├── docker-compose.yml
├── powerbi/POWERBI_SETUP.md
├── databricks/
└── docs/sops/
```

---

## Author

**Khushi Donda** — MS Applied Data Intelligence, San Jose State University  
[GitHub](https://github.com/khushidonda/lms-analytics-platform) | khushidonda.work@gmail.com
