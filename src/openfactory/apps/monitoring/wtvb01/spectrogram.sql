CREATE TABLE time_series_dx WITH (KAFKA_TOPIC='time_series_dx')
AS
SELECT
    ID,
    COLLECT_LIST(VALUE) AS value_list,
    COLLECT_LIST(TIMESTAMPTOSTRING(ROWTIME, 'yyyy-MM-dd''T''HH:mm:ss[.nnnnnnn]', 'Canada/Eastern')) AS timestamps
FROM assets_stream
WINDOW TUMBLING (SIZE 22 SECONDS)
WHERE ASSET_UUID = 'WTVB01' AND TYPE IN ('Events', 'Condition', 'Samples') AND VALUE != 'UNAVAILABLE' AND id = 'dx'
GROUP BY ID
EMIT CHANGES;

CREATE STREAM spectrogram_stream_dx (key VARCHAR, spectrogram_data ARRAY<ARRAY<DOUBLE>>) WITH (KAFKA_TOPIC='spectrogram_stream_dx', VALUE_FORMAT='JSON', PARTITIONS=1);
