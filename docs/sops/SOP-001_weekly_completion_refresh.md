# SOP-001: Weekly Completion Report Refresh

| Field | Value |
|-------|-------|
| **Trigger** | Every Monday, 9:00 AM PT |
| **Owner** | Project Owner |
| **Expected Duration** | 15 minutes |
| **Escalation** | Course / Program Coordinator |

## Steps

1. Verify Moodle Docker services are running: `docker compose ps`
2. Connect to reporting database (`data/lms.db`) via DBeaver or TablePlus
3. Run `sql/02_incomplete_courses.sql` — confirm row count is reasonable (students past due on core courses)
4. Run `sql/04_data_validation.sql` — all `issue_count` values should be 0
5. Export query results: `python seed/run_sql_exports.py`
6. Open Power BI dashboard (`powerbi/learning_engagement_dashboard.pbix`) and click **Refresh**
7. Verify KPI cards update: Completion Rate, Past-Due Count, Program On-Time Rate
8. Export Page 2 (Incomplete Courses drill-down) to PDF
9. Email PDF to program coordinator with subject: `Weekly Learning Completion Report — YYYY-MM-DD`

## Escalation Path

- If past-due row count = 0 unexpectedly → check data pipeline and Moodle service status
- If validation checks fail → halt report distribution, notify project coordinator
- If Power BI refresh fails → re-import CSVs from `data/processed/`

## Related Metrics

See `docs/DATA_LINEAGE.md` for field-level mapping of `completion_rate_pct`, `past_due_flag`, and `days_past_due`.
