# SOP-001: Weekly Compliance Report Refresh

| Field | Value |
|-------|-------|
| **Trigger** | Every Monday, 9:00 AM PT |
| **Owner** | Learning Analytics Intern |
| **Expected Duration** | 15 minutes |
| **Escalation** | Learning Technology Manager |

## Steps

1. Verify Moodle Docker services are running: `docker compose ps`
2. Connect to reporting database (`data/lms.db`) via DBeaver or TablePlus
3. Run `sql/02_overdue_compliance.sql` — confirm row count > 0
4. Run `sql/04_data_validation.sql` — all `issue_count` values should be 0
5. Export overdue report: `python seed/run_sql_exports.py`
6. Open Power BI dashboard (`powerbi/lms_dashboard.pbix`) and click **Refresh**
7. Verify KPI cards update: Completion Rate, Overdue Count, Compliance Score
8. Export Page 4 (Overdue Drill-Down) to PDF
9. Email PDF to HR team lead with subject: `Weekly Training Compliance — YYYY-MM-DD`

## Escalation Path

- If overdue row count = 0 unexpectedly → check data pipeline and Moodle service status
- If validation checks fail → halt report distribution, notify Learning Technology Manager
- If Power BI refresh fails → re-import CSVs from `data/processed/`
