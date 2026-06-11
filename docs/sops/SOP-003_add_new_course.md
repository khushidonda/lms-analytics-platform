# SOP-003: Adding a New Course to the LMS

| Field | Value |
|-------|-------|
| **Trigger** | Program coordinator approves request for new online course content |
| **Owner** | Project Owner |
| **Expected Duration** | 45–60 minutes |

## Steps

1. **Gather requirements** from stakeholder:
   - Course name, category (Core / Elective / Gen Ed)
   - Target programs, term due date, completion criteria
2. **Create course** in Moodle: Site Admin → Courses → Add new course
3. **Enable completion tracking**: Site Admin → Advanced Features → Completion tracking ON
4. **Define completion conditions**: view all sections + quiz pass threshold (≥ 80%)
5. **Upload content**: SCORM package, PDF, or Moodle quiz
6. **Configure enrollment**: manual enrollment for target programs
7. **Update course catalog**: `docs/COURSE_CATALOG.md`
8. **Update Power BI**: add course to program × course matrix filter in DAX
9. **Update data generator** (if using synthetic data): add course to `seed/generate_lms_data.py` and re-run
10. **Run validation**: confirm course appears in `sql/01_enrollment_summary.sql` output
11. **Document** change in project README or commit message

## Post-Launch

- Monitor completion rates for first 30 days
- Flag courses with < 50% completion at 14 days to program lead
- Refresh dashboard per SOP-001

## Related Files

| File | Purpose |
|------|---------|
| `docs/COURSE_CATALOG.md` | Canonical course list |
| `docs/DATA_LINEAGE.md` | Metric mapping after new course added |
| `sql/01_enrollment_summary.sql` | Validation query |
