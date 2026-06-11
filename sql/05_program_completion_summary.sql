-- Program-level completion summary for core courses

WITH core_status AS (
    SELECT
        u.program,
        c.fullname AS course_name,
        CASE
            WHEN cc.timecompleted IS NOT NULL
                 AND datetime(cc.timecompleted, 'unixepoch') <= ue.due_date
            THEN 'Completed On Time'
            WHEN cc.timecompleted IS NULL AND ue.due_date < date('now')
            THEN 'Past Due'
            WHEN cc.timecompleted IS NULL
            THEN 'In Progress'
            ELSE 'Completed Late'
        END AS completion_status
    FROM mdl_user u
    JOIN mdl_user_enrolments ue ON ue.userid = u.id
    JOIN mdl_enrol e ON e.id = ue.enrolid
    JOIN mdl_course c ON c.id = e.courseid
    LEFT JOIN mdl_course_completions cc
        ON cc.userid = u.id AND cc.course = c.id
    WHERE u.deleted = 0 AND c.is_core_course = 1
)
SELECT
    program,
    COUNT(*) AS core_enrollments,
    SUM(CASE WHEN completion_status = 'Completed On Time' THEN 1 ELSE 0 END) AS on_time_count,
    SUM(CASE WHEN completion_status = 'Past Due' THEN 1 ELSE 0 END) AS past_due_count,
    ROUND(
        100.0 * SUM(CASE WHEN completion_status = 'Completed On Time' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS on_time_rate_pct
FROM core_status
GROUP BY program
ORDER BY on_time_rate_pct ASC;
