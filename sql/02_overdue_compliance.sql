-- Overdue Compliance Report
-- Employee is overdue when due_date has passed and course is not completed.

SELECT
    u.id AS employee_id,
    u.firstname || ' ' || u.lastname AS full_name,
    u.email,
    u.department,
    c.fullname AS course_name,
    c.category,
    ue.due_date,
    CAST(julianday('now') - julianday(ue.due_date) AS INTEGER) AS days_overdue
FROM mdl_user u
JOIN mdl_user_enrolments ue ON ue.userid = u.id
JOIN mdl_enrol e ON e.id = ue.enrolid
JOIN mdl_course c ON c.id = e.courseid
LEFT JOIN mdl_course_completions cc
    ON cc.userid = u.id
   AND cc.course = c.id
WHERE u.deleted = 0
  AND c.compliance_required = 1
  AND ue.due_date < date('now')
  AND (cc.timecompleted IS NULL)
ORDER BY days_overdue DESC, u.department, full_name;
