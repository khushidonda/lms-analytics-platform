# Data Lineage — Online Learning Engagement Dashboard

This document maps every Power BI metric back to its source table, SQL transformation, and dashboard location. Use it for handoffs, audits, and documentation reviews.

---

## Metric Lineage Table

| Field / Metric | Source Table(s) | Source Field(s) | Transformation Applied | Output File / Query | Dashboard Location | Owner |
|----------------|-----------------|-----------------|------------------------|---------------------|-------------------|-------|
| `completion_rate_pct` | `mdl_course_completions`, `mdl_user_enrolments`, `mdl_enrol`, `mdl_course`, `mdl_user` | `timecompleted`, `userid`, `courseid` | `COUNT(completed) / COUNT(enrolled) × 100` via CTE in `01_enrollment_summary.sql` | `01_enrollment_summary.csv` | Page 1 KPI card, Page 2 program × course matrix | Project Owner |
| `past_due_flag` | `mdl_user_enrolments`, `mdl_course_completions`, `mdl_course` | `due_date`, `timecompleted`, `is_core_course` | `due_date < today AND timecompleted IS NULL AND is_core_course = 1` | `02_incomplete_courses.sql` → `02_incomplete_courses.csv` | Page 2 incomplete-students table | Project Owner |
| `days_past_due` | `mdl_user_enrolments` | `due_date` | `julianday(today) - julianday(due_date)` for rows where `past_due_flag = 1` | `02_incomplete_courses.csv` | Page 2 drill-down, sorted DESC | Project Owner |
| `days_to_complete` | `mdl_course_completions` | `timecompleted`, `timeenrolled` | `(timecompleted - timeenrolled) / 86400` (Unix seconds → days) | `01_enrollment_summary.csv` (`avg_days_to_complete`) | Page 3 scatter / distribution | Project Owner |
| `core_course_on_time_rate_pct` | `mdl_user`, `mdl_user_enrolments`, `mdl_course_completions`, `mdl_course` | `timecompleted`, `due_date`, `is_core_course` | `COUNT(on-time core completions) / COUNT(core enrollments) × 100` where on-time = completed before `due_date` | `05_program_completion_summary.sql` → `05_program_completion_summary.csv` | Page 1 bar chart by program | Project Owner |
| `engagement_risk_level` | Derived from `core_course_on_time_rate_pct` | — | `IF rate < 70% → RED`; `IF rate < 90% → YELLOW`; `ELSE GREEN` | Calculated in Power BI (DAX) from `05_program_completion_summary.csv` | Page 1 risk badges by program | Project Owner |
| `running_total_completions` | `mdl_course_completions`, `mdl_course` | `timecompleted`, `category` | `SUM(completions) OVER (PARTITION BY category ORDER BY completion_month)` | `03_participation_trend.sql` → `03_participation_trend.csv` | Page 3 trend line (running total overlay) | Project Owner |
| `avg_final_grade` | `mdl_grade_grades`, `mdl_user`, `mdl_course` | `finalgrade`, `userid`, `courseid` | `AVG(finalgrade)` grouped by program and course; filter `0 ≤ grade ≤ 100` | `mdl_grade_grades.csv` (joined in Power BI) | Page 2 grade column / Page 1 KPI | Project Owner |
| `data_quality_issue_count` | All core tables | varies by check | Four validation rules in `04_data_validation.sql`: completions before enrollment, orphaned enrollments, duplicate completions, grades out of range | `04_data_validation.csv` | Page 3 data quality panel (or appendix) | Project Owner |

---

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│  DATA SOURCES                                                           │
│  Kaggle-style online learning schema (inspiration)                      │
│  + Python generator (seed/generate_lms_data.py)                           │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  REPORTING WAREHOUSE                                                    │
│  SQLite: data/lms.db                                                    │
│  CSV exports: data/processed/mdl_*.csv                                  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                   ▼
┌──────────────────────────┐        ┌──────────────────────────┐
│  SQL TRANSFORM LAYER      │        │  MOODLE (optional Docker) │
│  sql/01–05 *.sql          │        │  seed/moodle_seed.php     │
│  CTEs + window functions  │        │  Live LMS demo at :8080   │
└─────────────┬────────────┘        └──────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ANALYTICS OUTPUTS                                                      │
│  data/processed/01_enrollment_summary.csv                               │
│  data/processed/02_incomplete_courses.csv                               │
│  data/processed/03_participation_trend.csv                              │
│  data/processed/04_data_validation.csv                                  │
│  data/processed/05_program_completion_summary.csv                       │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  POWER BI DASHBOARD                                                     │
│  powerbi/learning_engagement_dashboard.pbix                             │
│  Page 1: Overview KPIs + program completion                             │
│  Page 2: Program × course matrix + incomplete students                  │
│  Page 3: Monthly trends + data quality log                              │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  OPERATIONS & DOCUMENTATION                                             │
│  SOP-001: Weekly completion report refresh                              │
│  SOP-002: New student onboarding                                        │
│  SOP-003: Add new course                                                │
│  Weekly PDF export → program coordinator                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Entity Relationships (Reporting Model)

```
mdl_user (1) ──< (many) mdl_user_enrolments
mdl_user_enrolments >── (1) mdl_enrol ──< (many) mdl_course
mdl_user (1) ──< (many) mdl_course_completions ──> (1) mdl_course
mdl_user (1) ──< (many) mdl_grade_grades ──> (1) mdl_course
```

**Join keys used in SQL:**
- `mdl_user.id` = `mdl_user_enrolments.userid`
- `mdl_enrol.id` = `mdl_user_enrolments.enrolid`
- `mdl_enrol.courseid` = `mdl_course.id`
- `mdl_course_completions.userid` + `mdl_course_completions.course` → user + course

---

## Notes for Handoff

1. **Unix timestamps:** `mdl_course_completions.timecompleted` and `timeenrolled` are Unix integers. SQL converts with `datetime(col, 'unixepoch')` (SQLite) or `FROM_UNIXTIME()` (MySQL/MariaDB in Moodle).

2. **Incomplete enrollments:** `mdl_course_completions` only stores a row per enrollment attempt. A student who has not finished has `timecompleted IS NULL` — use `LEFT JOIN` + null check (see `02_incomplete_courses.sql`).

3. **Program field:** In production Moodle, program/college is often a custom profile field. In this project it lives on `mdl_user.program` for reporting simplicity. Moodle Docker seed maps `program` → `mdl_user.department`.

4. **Core vs elective:** `mdl_course.is_core_course = 1` replaces enterprise "mandatory training" flag. Past-due logic applies to core courses only.

5. **Refresh cadence:** Per SOP-001, run `python seed/run_sql_exports.py` then refresh Power BI every Monday. If using live Moodle data, export from MariaDB before running SQL.

6. **Validation gate:** Do not publish dashboard if `04_data_validation.csv` shows any `issue_count > 0`.

---

## Quick Reference: SQL File → Metrics Produced

| SQL file | Metrics / columns produced |
|----------|---------------------------|
| `01_enrollment_summary.sql` | `completion_rate_pct`, `avg_days_to_complete`, `total_enrolled`, `total_completed` |
| `02_incomplete_courses.sql` | `past_due_flag` (row existence), `days_past_due`, student + course detail |
| `03_participation_trend.sql` | `running_total_completions`, monthly `completions` by `category` |
| `04_data_validation.sql` | `data_quality_issue_count` (one row per check) |
| `05_program_completion_summary.sql` | `core_course_on_time_rate_pct`, `past_due_count`, `on_time_count` |

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| 2026-06 | Initial lineage for SJSU Data Visualization course project | Khushi Donda |
| 2026-06 | Expanded to 9-metric table + pipeline flow for documentation review | Khushi Donda |
