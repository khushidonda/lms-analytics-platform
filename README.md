# Online Learning Engagement Dashboard

**Khushi Donda** · MS Applied Data Intelligence · San Jose State University  
**Course project:** Data Visualization — Power BI dashboard on online learning data

---

## What is this?

A **medium-sized graduate school project** for my Data Visualization class. The professor asked us to build a Power BI dashboard from a real-world dataset. I found public **online learning / training** data on Kaggle, cleaned it in Python, analyzed it with SQL, and built an interactive dashboard.

Along the way I learned that this type of data often comes from **LMS platforms** (Moodle, Canvas, etc.), so I optionally explored Moodle in Docker to see how the underlying tables work.

**This is a class project — not a corporate LMS implementation.**

Read the full backstory: [`docs/PROJECT_STORY.md`](docs/PROJECT_STORY.md)

---

## Dataset (medium scope)

| | Count |
|---|------|
| Graduate students | 120 |
| Programs | 4 (SJSU MS programs) |
| Online courses | 6 |
| Enrollments | ~650 |

**Programs:** MS Business Analytics, MS Data Science, MS Information Systems, MS Applied Data Intelligence

---

## Tech stack

| Tool | Role in project |
|------|-----------------|
| **Power BI** | Main class deliverable (dashboard) |
| **SQL** | Enrollment, completion, and trend queries |
| **Python / Pandas** | Dataset generation and cleaning |
| **CSV / SQLite** | Data warehouse for analysis |
| **Moodle (Docker)** | Optional — explored LMS data model |
| **Databricks** | Bonus notebook for aggregation practice |

---

## Quick start

```bash
# 1. Generate data
python3 -m venv .venv && source .venv/bin/activate
pip install -r seed/requirements.txt
python seed/generate_lms_data.py
python seed/run_sql_exports.py

# 2. Build Power BI dashboard (main deliverable)
#    See powerbi/POWERBI_SETUP.md

# 3. Optional: explore Moodle locally
docker compose up -d
./seed/seed_moodle.sh
# http://localhost:8080 — admin / Admin123!
```

---

## Project structure

```
├── docs/
│   ├── PROJECT_STORY.md      # How the project started
│   ├── DATA_SOURCES.md       # Kaggle inspiration + synthetic data
│   ├── DATA_LINEAGE.md       # Full 9-metric lineage table
│   └── sops/                 # SOP-001 through SOP-003
├── seed/
│   ├── generate_lms_data.py  # Dataset generator
│   └── moodle_seed.php       # Optional Moodle loader
├── sql/                      # 5 analysis queries
├── data/processed/           # CSVs for Power BI
├── powerbi/POWERBI_SETUP.md
└── databricks/               # Bonus PySpark notebook
```

---

## Author

Khushi Donda — [GitHub](https://github.com/khushidonda/lms-analytics-platform)
