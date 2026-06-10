# SOP-003: Adding a New Course to the LMS

| Field | Value |
|-------|-------|
| **Trigger** | Intake request approved for new training content |
| **Owner** | Learning Analytics Intern |
| **Expected Duration** | 45–60 minutes |

## Steps

1. **Gather requirements** from stakeholder:
   - Course name, category (Mandatory / Elective / Onboarding)
   - Target departments, due date, completion criteria, recertification period
2. **Create course** in Moodle: Site Admin → Courses → Add new course
3. **Enable completion tracking**: Site Admin → Advanced Features → Completion tracking ON
4. **Define completion conditions**: view all sections + quiz pass threshold
5. **Upload content**: SCORM package, PDF, or Moodle quiz
6. **Configure enrollment**: manual enrollment for target departments
7. **Update course catalog**: `docs/COURSE_CATALOG.md` and `data/raw/course_catalog.csv`
8. **Update Power BI**: add course to compliance matrix filter in DAX
9. **Run validation**: confirm course appears in `sql/01_enrollment_summary.sql` output
10. **Document** in intake tracker and close request

## Post-Launch

- Monitor completion rates for first 30 days
- Flag courses with < 50% completion at 14 days to department lead
