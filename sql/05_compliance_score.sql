-- Department Compliance Score (mandatory courses only)

WITH mandatory_status AS (
    SELECT
        u.id AS user_id,
        u.department,
        c.id AS course_id,
        c.fullname AS course_name,
        CASE
            WHEN cc.timecompleted IS NOT NULL
                 AND datetime(cc.timecompleted, 'unixepoch') <= ue.due_date
            THEN 'Compliant'
            WHEN cc.timecompleted IS NULL AND ue.due_date < date('now')
            THEN 'Overdue'
            WHEN cc.timecompleted IS NULL
            THEN 'In Progress / Not Started'
            ELSE 'Completed Late'
        END AS compliance_status
    FROM mdl_user u
    JOIN mdl_user_enrolments ue ON ue.userid = u.id
    JOIN mdl_enrol e ON e.id = ue.enrolid
    JOIN mdl_course c ON c.id = e.courseid
    LEFT JOIN mdl_course_completions cc
        ON cc.userid = u.id
       AND cc.course = c.id
    WHERE u.deleted = 0
      AND c.compliance_required = 1
)
SELECT
    department,
    COUNT(*) AS mandatory_enrollments,
    SUM(CASE WHEN compliance_status = 'Compliant' THEN 1 ELSE 0 END) AS compliant_count,
    SUM(CASE WHEN compliance_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_count,
    ROUND(
        100.0 * SUM(CASE WHEN compliance_status = 'Compliant' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS compliance_rate_pct,
    CASE
        WHEN 100.0 * SUM(CASE WHEN compliance_status = 'Compliant' THEN 1 ELSE 0 END) / COUNT(*) < 70
        THEN 'RED'
        WHEN 100.0 * SUM(CASE WHEN compliance_status = 'Compliant' THEN 1 ELSE 0 END) / COUNT(*) < 90
        THEN 'YELLOW'
        ELSE 'GREEN'
    END AS compliance_risk_level
FROM mandatory_status
GROUP BY department
ORDER BY compliance_rate_pct ASC;
