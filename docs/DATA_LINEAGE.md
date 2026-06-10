# Data Lineage — LMS Analytics Platform

| Field / Metric | Source Table(s) | Transformation | Dashboard Location | Owner |
|----------------|-----------------|----------------|--------------------|-------|
| `completion_rate_pct` | `mdl_course_completions`, `mdl_user_enrolments` | `COUNT(completed) / COUNT(enrolled) * 100` | Page 1 KPI, Page 2 matrix | Learning Analytics Intern |
| `overdue_flag` | `mdl_user_enrolments`, `mdl_course_completions` | `due_date < today AND timecompleted IS NULL` | Page 4 overdue table | Learning Analytics Intern |
| `days_overdue` | `mdl_user_enrolments` | `julianday(today) - julianday(due_date)` | Page 4 drill-down | Learning Analytics Intern |
| `days_to_complete` | `mdl_course_completions` | `(timecompleted - timeenrolled) / 86400` | Page 3 scatter plot | Learning Analytics Intern |
| `compliance_rate_pct` | Mandatory enrollments only | Compliant / total mandatory * 100 | Page 1 bar chart | Learning Analytics Intern |
| `compliance_risk_level` | Derived from compliance rate | RED < 70%, YELLOW < 90%, else GREEN | Page 1 risk badges | Learning Analytics Intern |
| `running_total_completions` | `mdl_course_completions` | Window function `SUM() OVER (PARTITION BY category ORDER BY month)` | Page 3 trend line | Learning Analytics Intern |
| `intake_sla_days` | `mdl_intake_requests` | `resolved_date - created_date` | Page 5 intake tracker | Learning Analytics Intern |
| `data_quality_issue_count` | All core tables | Validation checks in `04_data_validation.sql` | Page 5 quality log | Learning Analytics Intern |

## Pipeline Flow

```
Moodle Admin UI (Docker)  →  Reporting Warehouse (SQLite / CSV)
         ↓                              ↓
   Course setup,                 SQL transformations
   enrollments,                  (CTEs, window functions)
   completion criteria                    ↓
                                   Power BI Dashboard
                                           ↓
                              SOPs + weekly PDF export to HR
```

## Notes for Handoff

- Moodle stores timestamps as Unix integers in production; this warehouse uses the same pattern in `mdl_course_completions`.
- `mdl_course_completions` only records completion when a user finishes — use `LEFT JOIN` + `NULL` check for not-started users.
- Department is stored as a custom profile field in production Moodle; here it lives on `mdl_user.department` for reporting simplicity.
