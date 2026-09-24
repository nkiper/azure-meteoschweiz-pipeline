SELECT COUNT(*) FROM [dim_stations]
SELECT TOP 5 * FROM [dim_stations]

SELECT COUNT(*) FROM [dim_parameters]
SELECT TOP 5 * FROM [dim_parameters]

SELECT COUNT(*) FROM [lf-ogd-smn_d_recent]

SELECT station_abbr, reference_timestamp, parameter, COUNT(*)
FROM [lf-ogd-smn_d_recent]
GROUP BY station_abbr, reference_timestamp, parameter
HAVING COUNT(*) > 1

SELECT COUNT(*) FROM [lf-ogd-smn_d_recent] WHERE station_id IS NULL OR parameter_id IS NULL;