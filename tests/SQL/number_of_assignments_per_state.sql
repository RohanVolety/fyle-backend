-- Write query to get the number of assignments for each state
SELECT state, COUNT(*) as assignment_count
FROM assignments
GROUP BY state
ORDER BY 1;