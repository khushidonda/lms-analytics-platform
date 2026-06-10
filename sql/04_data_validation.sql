-- Data Quality Validation Checks

SELECT 'completions_before_enrollment' AS check_name,
       COUNT(*) AS issue_count
FROM mdl_course_completions
WHERE timecompleted IS NOT NULL
  AND timecompleted < timeenrolled

UNION ALL

SELECT 'orphaned_enrollments' AS check_name,
       COUNT(*) AS issue_count
FROM mdl_user_enrolments ue
LEFT JOIN mdl_user u ON u.id = ue.userid
WHERE u.id IS NULL

UNION ALL

SELECT 'completions_missing_users' AS check_name,
       COUNT(*) AS issue_count
FROM mdl_course_completions cc
LEFT JOIN mdl_user u ON u.id = cc.userid
WHERE u.id IS NULL

UNION ALL

SELECT 'duplicate_completion_records' AS check_name,
       COUNT(*) - COUNT(DISTINCT userid || '-' || course) AS issue_count
FROM mdl_course_completions
WHERE timecompleted IS NOT NULL

UNION ALL

SELECT 'overdue_without_due_date' AS check_name,
       COUNT(*) AS issue_count
FROM mdl_user_enrolments
WHERE due_date IS NULL;
