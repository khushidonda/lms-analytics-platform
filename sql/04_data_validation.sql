-- Data quality checks before building the Power BI dashboard

SELECT 'completions_before_enrollment' AS check_name,
       COUNT(*) AS issue_count
FROM mdl_course_completions
WHERE timecompleted IS NOT NULL AND timecompleted < timeenrolled

UNION ALL

SELECT 'orphaned_enrollments',
       COUNT(*)
FROM mdl_user_enrolments ue
LEFT JOIN mdl_user u ON u.id = ue.userid
WHERE u.id IS NULL

UNION ALL

SELECT 'duplicate_completion_records',
       COUNT(*) - COUNT(DISTINCT userid || '-' || course)
FROM mdl_course_completions
WHERE timecompleted IS NOT NULL

UNION ALL

SELECT 'grades_out_of_range',
       COUNT(*)
FROM mdl_grade_grades
WHERE finalgrade < 0 OR finalgrade > 100;
