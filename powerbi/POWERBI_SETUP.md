# Power BI Dashboard Setup Guide

Build a 5-page dashboard using the pre-computed CSVs in `data/processed/`.

## Step 1: Import Data

Open Power BI Desktop → **Get Data** → **Text/CSV** and import:

| File | Purpose |
|------|---------|
| `05_compliance_score.csv` | Department compliance KPIs |
| `01_enrollment_summary.csv` | Enrollment/completion matrix |
| `02_overdue_compliance.csv` | Overdue employee drill-down |
| `03_participation_trend.csv` | Monthly trend lines |
| `04_data_validation.csv` | Data quality log |
| `mdl_intake_requests.csv` | Intake request tracker |
| `mdl_user.csv` | Employee dimension |
| `mdl_course.csv` | Course dimension |

## Step 2: Data Model Relationships

```
mdl_user[id] ──< 02_overdue_compliance[employee_id]
mdl_course[fullname] ── 01_enrollment_summary[course_name]
mdl_user[department] ── 05_compliance_score[department]
```

## Step 3: DAX Measures

```dax
Completion Rate % =
DIVIDE(
    SUM('01_enrollment_summary'[total_completed]),
    SUM('01_enrollment_summary'[total_enrolled])
)

Overdue Count =
COUNTROWS('02_overdue_compliance')

Avg Days to Complete =
AVERAGE('01_enrollment_summary'[avg_days_to_complete])

Fully Compliant Employees =
CALCULATE(
    DISTINCTCOUNT('mdl_user'[id]),
    FILTER(
        '05_compliance_score',
        '05_compliance_score'[overdue_count] = 0
    )
)

Compliance Risk Level =
SWITCH(
    TRUE(),
    [Completion Rate %] < 0.70, "RED",
    [Completion Rate %] < 0.90, "YELLOW",
    "GREEN"
)

Intake SLA Days =
AVERAGE(
    DATEDIFF(
        'mdl_intake_requests'[created_date],
        'mdl_intake_requests'[resolved_date],
        DAY
    )
)
```

## Step 4: Dashboard Pages

### Page 1 — Executive Overview
- KPI cards: Completion Rate %, Overdue Count, Fully Compliant Employees
- Bar chart: Compliance rate by department (from `05_compliance_score`)
- Risk badges: RED / YELLOW / GREEN by department

### Page 2 — Compliance Matrix
- Matrix: Department (rows) × Course (columns) → Completion Rate %
- Conditional formatting: red < 70%, yellow 70–90%, green > 90%

### Page 3 — Participation Trends
- Line chart: Monthly completions by category (`03_participation_trend`)
- Running total overlay per category

### Page 4 — Overdue Drill-Down
- Table: full_name, department, course_name, due_date, days_overdue
- Slicer: department, course
- Sort by days_overdue DESC

### Page 5 — Operations & Data Quality
- Intake request table with status and SLA
- Data validation check results from `04_data_validation`
- Open vs Resolved intake count

## Step 5: Save

Save as `powerbi/lms_dashboard.pbix` and add screenshots to README.
