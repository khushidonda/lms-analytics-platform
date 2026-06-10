-- Enrollment & Completion Summary by Department
-- Mirrors Moodle 4.3 reporting pattern (mdl_user, mdl_enrol, mdl_user_enrolments, mdl_course_completions)

WITH base_enrollments AS (
    SELECT
        u.id AS user_id,
        u.department,
        c.id AS course_id,
        c.fullname AS course_name,
        c.category,
        ue.timestart AS enrolled_unix,
        cc.timecompleted AS completed_unix
    FROM mdl_user u
    JOIN mdl_user_enrolments ue ON ue.userid = u.id
    JOIN mdl_enrol e ON e.id = ue.enrolid
    JOIN mdl_course c ON c.id = e.courseid
    LEFT JOIN mdl_course_completions cc
        ON cc.userid = u.id
       AND cc.course = c.id
    WHERE u.deleted = 0
),
completion_agg AS (
    SELECT
        department,
        course_name,
        category,
        COUNT(*) AS total_enrolled,
        SUM(CASE WHEN completed_unix IS NOT NULL THEN 1 ELSE 0 END) AS total_completed,
        ROUND(
            100.0 * SUM(CASE WHEN completed_unix IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*),
            1
        ) AS completion_rate_pct,
        ROUND(
            AVG(
                CASE
                    WHEN completed_unix IS NOT NULL
                    THEN (completed_unix - enrolled_unix) / 86400.0
                END
            ),
            1
        ) AS avg_days_to_complete
    FROM base_enrollments
    GROUP BY department, course_name, category
)
SELECT *
FROM completion_agg
ORDER BY department, course_name;
