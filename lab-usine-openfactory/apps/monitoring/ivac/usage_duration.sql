-- Create a stream to capture power events for IVAC assets
CREATE STREAM IF NOT EXISTS ivac_power_events WITH (KAFKA_TOPIC='power_events', PARTITIONS=1) AS
SELECT
    id AS key,
    asset_uuid,
    value,
    ROWTIME AS ts
FROM ASSETS_STREAM
WHERE asset_uuid = 'IVAC' AND id IN ('A1ToolPlus', 'A2ToolPlus', 'A3ToolPlus')
EMIT CHANGES;

-- Create a table to keep track of the latest power state for each IVAC asset
CREATE TABLE IF NOT EXISTS latest_ivac_power_state AS
SELECT
    key,
    LATEST_BY_OFFSET(value) AS last_value,
    LATEST_BY_OFFSET(ts) AS last_ts
FROM ivac_power_events
GROUP BY key;

-- Create a stream to calculate the duration of each power state change
CREATE STREAM IF NOT EXISTS ivac_power_durations AS
SELECT
    ivac_event.key,
    s.last_value AS state_just_ended,
    (ivac_event.ts - s.last_ts) / 1000 AS duration_sec
FROM ivac_power_events ivac_event
JOIN latest_ivac_power_state s
    ON ivac_event.key = s.key
WHERE ivac_event.value IS DISTINCT FROM s.last_value
EMIT CHANGES;


-- Create a table to summarize the total duration and count of state changes for each IVAC power state
CREATE TABLE IF NOT EXISTS ivac_power_state_totals AS
SELECT
    CONCAT(IVAC_EVENT_KEY, '_', STATE_JUST_ENDED) AS ivac_power_key,
    SUM(DURATION_SEC) AS total_duration_sec,
    COUNT(*) AS state_change_count
FROM ivac_power_durations
GROUP BY CONCAT(IVAC_EVENT_KEY, '_', STATE_JUST_ENDED)
EMIT CHANGES;