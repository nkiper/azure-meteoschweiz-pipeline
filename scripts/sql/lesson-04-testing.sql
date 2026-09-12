SELECT * FROM sys.tables WHERE name = 'ogd-smn_d_recent';

SELECT station_abbr, COUNT(*) as count FROM [ogd-smn_d_recent] GROUP BY station_abbr;

SELECT * FROM sys.dm_exec_sessions WHERE is_user_process = 1;
SELECT * FROM sys.dm_tran_active_transactions;

SET SHOWPLAN_TEXT ON;
SELECT * FROM [ogd-smn_d_recent]
WHERE station_abbr = 'beh' AND reference_timestamp = '2024-01-01 00:00:00';

SELECT COUNT(DISTINCT station_abbr) AS station_count, COUNT(*) AS total_rows
FROM [ogd-smn_d_recent];
