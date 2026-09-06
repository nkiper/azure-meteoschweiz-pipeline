SELECT COUNT(*) FROM [ogd-smn_beh_d_recent];
SELECT MIN(reference_timestamp) FROM [ogd-smn_beh_d_recent];
SELECT MAX(reference_timestamp) FROM [ogd-smn_beh_d_recent];
SELECT COUNT(DISTINCT COLUMN_NAME) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'ogd-smn_beh_d_recent';
SELECT COUNT(station_abbr) FROM [ogd-smn_beh_d_recent] where station_abbr IS NULL;
SELECT COUNT(reference_timestamp) FROM [ogd-smn_beh_d_recent] where reference_timestamp IS NULL;

SELECT top 10 * FROM [ogd-smn_beh_d_recent] WHERE station_abbr = 'BEH';

SELECT * FROM [ogd-smn_beh_d_recent] WHERE station_abbr = 'BEH' ORDER BY reference_timestamp ASC;

SELECT station_abbr, COUNT(*) as count FROM [ogd-smn_beh_d_recent] GROUP BY station_abbr;