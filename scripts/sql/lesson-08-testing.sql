SELECT station_data_since FROM dim_stations WHERE station_abbr='BLA';

DELETE FROM [lf-ogd-smn_d] WHERE YEAR(reference_timestamp) < 2006;
SELECT COUNT(*) FROM [lf-ogd-smn_d] WHERE YEAR(reference_timestamp) < 2026;

DBCC SHRINKDATABASE (0);

SELECT COUNT(*) FROM [dim_month];
SELECT MIN(full_month_date), MAX(full_month_date) FROM [dim_month];

SELECT COUNT(*) FROM [lf-ogd-smn_m];

SELECT COLUMN_NAME
FROM information_schema.columns
WHERE table_name = 'lf-ogd-smn_m';

SELECT ccu.COLUMN_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu ON tc.CONSTRAINT_NAME = ccu.CONSTRAINT_NAME
WHERE tc.TABLE_NAME = 'lf-ogd-smn_m' AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY';