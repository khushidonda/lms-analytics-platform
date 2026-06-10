# SOP-002: New Employee LMS Onboarding

| Field | Value |
|-------|-------|
| **Trigger** | HR notifies Learning Technology of new hire |
| **Owner** | Learning Analytics Intern |
| **Expected Duration** | 20 minutes |

## Steps

1. Receive new hire details from HR: name, email, department, start date, role
2. Log into Moodle Admin at `http://localhost:8080` (Site Admin → Users → Add new user)
3. Create user account with company email and assign to correct department
4. Enroll user in onboarding bundle:
   - LMS Platform Orientation (due: 30 days from start)
   - All mandatory compliance courses (due: per course calendar)
5. Set completion deadlines in Moodle course settings
6. Verify enrollment in database: check `mdl_user_enrolments` for new records
7. Update employee roster CSV: `data/raw/employee_roster.csv`
8. Confirm user receives Moodle enrollment notification email (if SMTP configured)
9. Log intake request as Resolved in intake tracker

## Verification Checklist

- [ ] User appears in Moodle user list
- [ ] All mandatory courses show as enrolled
- [ ] Due dates are set correctly
- [ ] Enrollment visible in reporting warehouse after next data refresh
