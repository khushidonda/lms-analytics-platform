# SOP-002: New Student LMS Onboarding

| Field | Value |
|-------|-------|
| **Trigger** | Registrar / program coordinator notifies team of new student enrollment |
| **Owner** | Project Owner |
| **Expected Duration** | 20 minutes |

## Steps

1. Receive new student details: name, email, program, cohort start date, student level
2. Log into Moodle Admin at `http://localhost:8080` (Site Admin → Users → Add new user)
3. Create user account with `@sjsu.edu` email and assign to correct program (department field)
4. Enroll student in onboarding bundle:
   - LMS Platform Orientation (due: 30 days from cohort start)
   - All core course requirements (due: per course term calendar)
5. Set completion deadlines in Moodle course settings
6. Verify enrollment in database: check `mdl_user_enrolments` for new records
7. Update student roster CSV: `data/processed/mdl_user.csv` (after next generator run if bulk)
8. Confirm student receives Moodle enrollment notification email (if SMTP configured)
9. Log support request as Resolved in tracker (if applicable)

## Verification Checklist

- [ ] Student appears in Moodle user list
- [ ] All core courses show as enrolled
- [ ] Due dates are set correctly
- [ ] Enrollment visible in reporting warehouse after next data refresh (`python seed/run_sql_exports.py`)

## Related Documentation

- Course list: `docs/COURSE_CATALOG.md`
- Data lineage: `docs/DATA_LINEAGE.md`
