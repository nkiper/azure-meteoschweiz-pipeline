SELECT COUNT(*) FROM [dim_date];
SELECT TOP 5 * FROM [dim_date] ORDER BY full_date;

SELECT COUNT(*) FROM [lf-ogd-smn_d_recent];

SELECT station_abbr, reference_timestamp, parameter, COUNT(*)
FROM [lf-ogd-smn_d_recent]
GROUP BY station_abbr, reference_timestamp, parameter
HAVING COUNT(*) > 1

SELECT COUNT(*) FROM [lf-ogd-smn_d_recent]
WHERE station_id IS NULL OR parameter_id IS NULL OR date_id IS NULL;