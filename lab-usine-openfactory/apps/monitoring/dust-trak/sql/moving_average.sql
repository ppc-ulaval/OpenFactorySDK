CREATE TABLE pm1_concentration_moving_average AS
SELECT
    ASSET_UUID, 
    AVG(CAST(VALUE AS DOUBLE)) AS average_value,
    TIMESTAMPTOSTRING(WINDOWEND, 'yyyy-MM-dd''T''HH:mm:ss[.nnnnnnn]', 'Canada/Eastern') AS TIMESTAMP
FROM assets_stream
WINDOW HOPPING (SIZE 10 SECONDS, ADVANCE BY 5 SECONDS)
WHERE ASSET_UUID = 'DUSTTRAK' AND TYPE IN ('Events', 'Condition', 'Samples') AND VALUE != 'UNAVAILABLE' AND id = 'pm1_concentration'
GROUP BY ASSET_UUID
EMIT CHANGES;

CREATE TABLE pm2_5_concentration_moving_average AS
SELECT
    ASSET_UUID, 
    AVG(CAST(VALUE AS DOUBLE)) AS average_value,
    TIMESTAMPTOSTRING(WINDOWEND, 'yyyy-MM-dd''T''HH:mm:ss[.nnnnnnn]', 'Canada/Eastern') AS TIMESTAMP
FROM assets_stream
WINDOW HOPPING (SIZE 10 SECONDS, ADVANCE BY 5 SECONDS)
WHERE ASSET_UUID = 'DUSTTRAK' AND TYPE IN ('Events', 'Condition', 'Samples') AND VALUE != 'UNAVAILABLE' AND id = 'pm2_5_concentration'
GROUP BY ASSET_UUID
EMIT CHANGES;

CREATE TABLE pm4_concentration_moving_average AS
SELECT
    ASSET_UUID,
    AVG(CAST(VALUE AS DOUBLE)) AS average_value,
    TIMESTAMPTOSTRING(WINDOWEND, 'yyyy-MM-dd''T''HH:mm:ss[.nnnnnnn]', 'Canada/Eastern') AS TIMESTAMP
FROM assets_stream
WINDOW HOPPING (SIZE 10 SECONDS, ADVANCE BY 5 SECONDS)
WHERE ASSET_UUID = 'DUSTTRAK' AND TYPE IN ('Events', 'Condition', 'Samples') AND VALUE != 'UNAVAILABLE' AND id = 'pm4_concentration'
GROUP BY ASSET_UUID
EMIT CHANGES;

CREATE TABLE pm10_concentration_moving_average AS
SELECT
    ASSET_UUID, 
    AVG(CAST(VALUE AS DOUBLE)) AS average_value,
    TIMESTAMPTOSTRING(WINDOWEND, 'yyyy-MM-dd''T''HH:mm:ss[.nnnnnnn]', 'Canada/Eastern') AS TIMESTAMP
FROM assets_stream
WINDOW HOPPING (SIZE 10 SECONDS, ADVANCE BY 5 SECONDS)
WHERE ASSET_UUID = 'DUSTTRAK' AND TYPE IN ('Events', 'Condition', 'Samples') AND VALUE != 'UNAVAILABLE' AND id = 'pm10_concentration'
GROUP BY ASSET_UUID
EMIT CHANGES;