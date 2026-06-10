-- Training Participation Trend (Monthly completions by course category)

WITH monthly_completions AS (
    SELECT
        strftime('%Y-%m', datetime(cc.timecompleted, 'unixepoch')) AS completion_month,
        c.category,
        COUNT(*) AS completions
    FROM mdl_course_completions cc
    JOIN mdl_course c ON c.id = cc.course
    WHERE cc.timecompleted IS NOT NULL
      AND datetime(cc.timecompleted, 'unixepoch') >= datetime('now', '-12 months')
    GROUP BY completion_month, c.category
)
SELECT
    completion_month,
    category,
    completions,
    SUM(completions) OVER (
        PARTITION BY category
        ORDER BY completion_month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total_completions
FROM monthly_completions
ORDER BY category, completion_month;
