# Data Lineage

| Dashboard metric | Source | Transformation | Power BI page |
|------------------|--------|----------------|---------------|
| Completion rate % | `mdl_course_completions` | completed / enrolled × 100 | Overview |
| Avg days to complete | enroll + completion timestamps | date difference | Course detail |
| Past-due count | `mdl_user_enrolments` + completions | due_date passed, no completion | At-risk students |
| Monthly completions | `mdl_course_completions` | group by month + category | Trends |
| Program on-time rate | core courses only | on-time / total core enrollments | By program |

## Pipeline

```
Kaggle-style schema (inspired)
        ↓
Python generator (seed/generate_lms_data.py)
        ↓
SQLite + CSV exports (data/processed/)
        ↓
SQL queries (sql/*.sql)
        ↓
Power BI dashboard (main class deliverable)
```
