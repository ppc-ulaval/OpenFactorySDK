-- Check if corresponding gates and tools have compatible states
CREATE TABLE latest_tool_states AS
SELECT 
    SUBSTRING(id, 1, 2) AS equipment_group,
    LATEST_BY_OFFSET(value) as current_value,
    LATEST_BY_OFFSET(attributes) as current_attributes
FROM ASSETS_STREAM
WHERE asset_uuid = 'IVAC' AND id IN ('A1ToolPlus', 'A2ToolPlus', 'A3ToolPlus')
GROUP BY SUBSTRING(id, 1, 2)
EMIT CHANGES;

CREATE TABLE latest_gate_states AS
SELECT 
    SUBSTRING(id, 1, 2) AS equipment_group,
    LATEST_BY_OFFSET(value) as current_value,
    LATEST_BY_OFFSET(attributes) as current_attributes
FROM ASSETS_STREAM
WHERE asset_uuid = 'IVAC' AND id IN ('A1BlastGate', 'A2BlastGate', 'A3BlastGate')
GROUP BY SUBSTRING(id, 1, 2)
EMIT CHANGES;

CREATE TABLE equipment_group_states AS
SELECT
    tools.equipment_group as equipment_group,
    gates.current_value as gate_state,
    tools.current_value as tool_state
FROM
latest_gate_states gates JOIN latest_tool_states tools 
ON gates.equipment_group = tools.equipment_group
EMIT CHANGES;


CREATE TABLE tool_gate_violations AS
SELECT
    gate_state,
    tool_state,
    equipment_group,
    CASE 
        WHEN tool_state = 'ON' AND gate_state = 'CLOSED' THEN 'TOOL_ON_GATE_OFF'
        ELSE 'TOOL_OFF_GATE_ON'
    END as violation_type,
    CASE 
        WHEN tool_state = 'ON' AND gate_state = 'CLOSED' THEN CONCAT('Tool ', equipment_group, ' is ON but Gate ', equipment_group, ' is ', gate_state, ' - Gate should be OPEN')
        ELSE CONCAT('Tool ', equipment_group, ' is OFF but Gate ', equipment_group, ' is OPEN - Gate should be CLOSED')
    END as violation_message,
    TIMESTAMPTOSTRING(ROWTIME, 'yyyy-MM-dd''T''HH:mm:ss[.nnnnnnn]', 'Canada/Eastern') as violation_timestamp
FROM equipment_group_states
WHERE 
    (tool_state = 'ON' AND gate_state = 'CLOSED') OR
    (tool_state = 'OFF' AND gate_state = 'OPEN')
EMIT CHANGES;

CREATE STREAM tool_gate_violations_stream (
    equipment_group STRING KEY,
    violation_type STRING,
    violation_message STRING,
    violation_timestamp STRING
) WITH (
    KAFKA_TOPIC='TOOL_GATE_VIOLATIONS',
    VALUE_FORMAT='JSON'
);



--Check if at least one gate is open, at least one gate is closed and if at least one tool is off  at all times 
CREATE STREAM latest_tool_states_stream AS
SELECT
    id AS tool_id,
    value AS current_value,
    attributes AS current_attributes,
    asset_uuid,
    ROWTIME AS event_time
FROM ASSETS_STREAM
WHERE asset_uuid = 'IVAC' AND id IN ('A1ToolPlus', 'A2ToolPlus', 'A3ToolPlus')
EMIT CHANGES;

CREATE STREAM latest_gate_states_stream AS
SELECT
    id AS gate_id,
    value AS current_value,
    attributes AS current_attributes,
    asset_uuid,
    ROWTIME AS event_time
FROM ASSETS_STREAM
WHERE asset_uuid = 'IVAC'
  AND id IN ('A1BlastGate', 'A2BlastGate', 'A3BlastGate')
EMIT CHANGES;

CREATE STREAM A1_ON AS
SELECT * FROM latest_tool_states_stream
WHERE tool_id = 'A1ToolPlus' AND current_value = 'ON';

CREATE STREAM A2_ON AS
SELECT * FROM latest_tool_states_stream
WHERE tool_id = 'A2ToolPlus' AND current_value = 'ON';

CREATE STREAM A3_ON AS
SELECT * FROM latest_tool_states_stream
WHERE tool_id = 'A3ToolPlus' AND current_value = 'ON';

CREATE STREAM A1_OPEN AS
SELECT * FROM latest_gate_states_stream
WHERE gate_id = 'A1BlastGate' AND current_value = 'OPEN';

CREATE STREAM A2_OPEN AS
SELECT * FROM latest_gate_states_stream
WHERE gate_id = 'A2BlastGate' AND current_value = 'OPEN';

CREATE STREAM A3_OPEN AS
SELECT * FROM latest_gate_states_stream
WHERE gate_id = 'A3BlastGate' AND current_value = 'OPEN';

CREATE STREAM A1_CLOSED AS
SELECT * FROM latest_gate_states_stream
WHERE gate_id = 'A1BlastGate' AND current_value = 'CLOSED';

CREATE STREAM A2_CLOSED AS
SELECT * FROM latest_gate_states_stream
WHERE gate_id = 'A2BlastGate' AND current_value = 'CLOSED';

CREATE STREAM A3_CLOSED AS
SELECT * FROM latest_gate_states_stream
WHERE gate_id = 'A3BlastGate' AND current_value = 'CLOSED';

CREATE STREAM all_tools_on_violation AS
SELECT
    A1.asset_uuid as asset_uuid,
    A1.ROWTIME AS violation_timestamp,
    'ALL_TOOLS_ON' AS violation_type,
    'All ToolPlus units are ON simultaneously: system overload or misconfiguration' AS violation_message
FROM A1_ON A1
JOIN A2_ON A2 WITHIN 2 SECONDS GRACE PERIOD 1 SECOND ON A1.asset_uuid = A2.asset_uuid
JOIN A3_ON A3 WITHIN 2 SECONDS GRACE PERIOD 1 SECOND ON A1.asset_uuid = A3.asset_uuid
EMIT CHANGES;


CREATE STREAM all_gates_open_violation AS
SELECT
    A1.asset_uuid as asset_uuid,
    A1.ROWTIME AS violation_timestamp,
    'ALL_GATES_OPEN' AS violation_type,
    'All Blast Gates are OPEN simultaneously: airflow loss or system misconfiguration' AS violation_message
FROM A1_OPEN A1
JOIN A2_OPEN A2 WITHIN 2 SECONDS GRACE PERIOD 1 SECOND ON A1.asset_uuid = A2.asset_uuid
JOIN A3_OPEN A3 WITHIN 2 SECONDS GRACE PERIOD 1 SECOND ON A1.asset_uuid = A3.asset_uuid
EMIT CHANGES;

CREATE STREAM all_gates_closed_violation AS
SELECT
    A1.asset_uuid as asset_uuid,
    A1.ROWTIME AS violation_timestamp,
    'ALL_GATES_CLOSED' AS violation_type,
    'All Blast Gates are CLOSED simultaneously: system misconfiguration' AS violation_message
FROM A1_OPEN A1
JOIN A2_OPEN A2 WITHIN 2 SECONDS GRACE PERIOD 1 SECOND ON A1.asset_uuid = A2.asset_uuid
JOIN A3_OPEN A3 WITHIN 2 SECONDS GRACE PERIOD 1 SECOND ON A1.asset_uuid = A3.asset_uuid
EMIT CHANGES;

CREATE STREAM ivac_violations (
    asset_uuid STRING KEY,
    violation_timestamp STRING,
    equipment_group STRING,
    violation_type STRING,
    violation_message STRING
) WITH (
    KAFKA_TOPIC='ivac_violations',
    PARTITIONS=1,
    VALUE_FORMAT='JSON'
);

CREATE STREAM ivac_violations1
WITH (KAFKA_TOPIC='ivac_violations')
AS SELECT
    asset_uuid,
    TIMESTAMPTOSTRING(violation_timestamp, 'yyyy-MM-dd''T''HH:mm:ss.SSS', 'Canada/Eastern') AS violation_timestamp,
    CAST(NULL as VARCHAR) AS equipment_group,
    violation_type,
    violation_message
FROM all_tools_on_violation
EMIT CHANGES;

CREATE STREAM ivac_violations2
WITH (KAFKA_TOPIC='ivac_violations')
AS SELECT
    asset_uuid,
    TIMESTAMPTOSTRING(violation_timestamp, 'yyyy-MM-dd''T''HH:mm:ss.SSS', 'Canada/Eastern') AS violation_timestamp,
    CAST(NULL as VARCHAR) AS equipment_group,
    violation_type,
    violation_message
FROM all_gates_open_violation
EMIT CHANGES;

CREATE STREAM ivac_violations3
WITH (KAFKA_TOPIC='ivac_violations')
AS SELECT 
    asset_uuid,
    TIMESTAMPTOSTRING(violation_timestamp, 'yyyy-MM-dd''T''HH:mm:ss.SSS', 'Canada/Eastern') AS violation_timestamp,
    CAST(NULL as VARCHAR) AS equipment_group,
    violation_type,
    violation_message
FROM all_gates_closed_violation
EMIT CHANGES;

CREATE STREAM ivac_violations4
WITH (KAFKA_TOPIC='ivac_violations')
AS SELECT
    'IVAC' as asset_uuid,
    violation_timestamp,
    equipment_group,
    violation_type,
    violation_message
FROM tool_gate_violations_stream
PARTITION BY 'IVAC'
EMIT CHANGES;
