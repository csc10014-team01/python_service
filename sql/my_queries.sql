-- F2: Average time taken per intent, rounded to 1 decimal place
SELECT
    intent,
    ROUND(AVG(latency_ms), 1) AS avg_latency
FROM interaction
GROUP BY intent;

-- F3: Which topics got the most thumbs-down?
SELECT
    i.topic,
    COUNT(*) AS thumbs_down_count
FROM interaction AS i
JOIN feedback AS f
    ON f.request_id = i.request_id
WHERE f.rating = -1
    AND i.topic IS NOT NULL
GROUP BY i.topic
ORDER BY thumbs_down_count DESC, i.topic ASC;