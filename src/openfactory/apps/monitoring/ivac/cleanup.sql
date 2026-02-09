--usage_duration.sql
DROP TABLE IF EXISTS ivac_power_state_totals;
DROP STREAM IF EXISTS ivac_power_durations;
DROP TABLE IF EXISTS latest_ivac_power_state;
DROP STREAM IF EXISTS ivac_power_events;

-- system_health.sql
DROP STREAM IF EXISTS ivac_violations4;
DROP STREAM IF EXISTS ivac_violations3;
DROP STREAM IF EXISTS ivac_violations2;
DROP STREAM IF EXISTS ivac_violations1;
DROP STREAM IF EXISTS ivac_violations;
DROP STREAM IF EXISTS all_gates_closed_violation;
DROP STREAM IF EXISTS all_gates_open_violation;
DROP STREAM IF EXISTS all_tools_on_violation;
DROP STREAM IF EXISTS A3_CLOSED;
DROP STREAM IF EXISTS A2_CLOSED;
DROP STREAM IF EXISTS A1_CLOSED;
DROP STREAM IF EXISTS A3_OPEN;
DROP STREAM IF EXISTS A2_OPEN;
DROP STREAM IF EXISTS A1_OPEN;
DROP STREAM IF EXISTS A3_ON;
DROP STREAM IF EXISTS A2_ON;
DROP STREAM IF EXISTS A1_ON;
DROP STREAM IF EXISTS latest_gate_states_stream;
DROP STREAM IF EXISTS latest_tool_states_stream;
DROP STREAM IF EXISTS tool_gate_violations_stream;
DROP TABLE IF EXISTS tool_gate_violations;
DROP TABLE IF EXISTS equipment_group_states;
DROP TABLE IF EXISTS latest_gate_states;
DROP TABLE IF EXISTS latest_tool_states;