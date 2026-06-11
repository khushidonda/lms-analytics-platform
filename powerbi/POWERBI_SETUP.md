# Power BI Dashboard — Class Project Setup

**Course:** Data Visualization (SJSU)  
**Deliverable:** 3-page interactive dashboard

## Step 1: Import CSVs

Power BI Desktop → **Get Data** → **Text/CSV**:

| File | Use for |
|------|---------|
| `01_enrollment_summary.csv` | Program × course completion matrix |
| `02_incomplete_courses.csv` | Students past due on core courses |
| `03_participation_trend.csv` | Monthly completion trend lines |
| `05_program_completion_summary.csv` | Program-level KPIs |
| `mdl_user.csv` | Student dimension (program, cohort) |
| `mdl_course.csv` | Course dimension |
| `mdl_grade_grades.csv` | Average grade visuals |

## Step 2: Relationships

```
mdl_user[id] ──< 02_incomplete_courses[student_id]
mdl_user[program] ── 01_enrollment_summary[program]
mdl_course[fullname] ── 01_enrollment_summary[course_name]
```

## Step 3: DAX measures

```dax
Completion Rate % =
DIVIDE(
    SUM('01_enrollment_summary'[total_completed]),
    SUM('01_enrollment_summary'[total_enrolled])
)

Past Due Students =
COUNTROWS('02_incomplete_courses')

Avg Grade =
AVERAGE(mdl_grade_grades[finalgrade])

Avg Days to Complete =
AVERAGE('01_enrollment_summary'[avg_days_to_complete])
```

## Step 4: Three dashboard pages

### Page 1 — Overview
- KPI cards: total students, overall completion %, past-due count, avg grade
- Bar chart: completion rate by program
- Donut: enrollments by course category (Core / Elective / Gen Ed)

### Page 2 — Program & Course Detail
- Matrix: program (rows) × course (columns) → completion %
- Table: incomplete courses with days past due
- Conditional formatting: red below 70%, yellow 70–85%, green above 85%

### Page 3 — Trends
- Line chart: monthly completions from `03_participation_trend`
- Running total by category
- Slicer: program, course category

## Step 5: Save

Save as `powerbi/learning_engagement_dashboard.pbix` and export screenshots for your course submission.
