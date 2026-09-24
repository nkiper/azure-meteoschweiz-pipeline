-- write a query that returns station_name, reference_timestamp, parameter, and value for station BEH only, 
-- joining [lf-ogd-smn_d_recent] to dim_stations

SELECT b.station_name, a.reference_timestamp, a.parameter, a.value
FROM [lf-ogd-smn_d_recent] a
JOIN [dim_stations] b ON a.station_id = b.station_id
WHERE b.station_abbr = 'BEH'

-- extend your query to also pull in parameter_unit from dim_parameters

SELECT b.station_name, a.reference_timestamp, a.parameter, a.value, c.parameter_unit
FROM [lf-ogd-smn_d_recent] a
JOIN [dim_stations] b ON a.station_id = b.station_id
JOIN [dim_parameters] c ON a.parameter_id = c.parameter_id
WHERE b.station_abbr = 'BEH'

-- write a CTE called high_elevation_stations that selects station_id, station_name from dim_stations where 
-- height_masl > 1000. Then, in the main query below it, join that CTE against your fact table (and 
-- dim_parameters, if you want the unit too) to compute the average value per parameter, grouped by 
-- parameter — only for those high-elevation stations.

WITH high_elevation_stations AS (
    SELECT station_id, station_name
    FROM dim_stations
    WHERE station_height_masl > 1000
)
SELECT b.parameter, AVG(b.value)
FROM high_elevation_stations a
JOIN [lf-ogd-smn_d_recent] b ON a.station_id = b.station_id
GROUP BY b.parameter;

WITH high_elevation_stations AS (
    SELECT station_id, station_name
    FROM dim_stations
    WHERE station_height_masl > 1000
)
SELECT b.parameter, AVG(b.value), c.parameter_unit
FROM high_elevation_stations a
JOIN [lf-ogd-smn_d_recent] b ON a.station_id = b.station_id
JOIN [dim_parameters] c ON b.parameter_id = c.parameter_id
GROUP BY b.parameter, c.parameter_unit

-- write a query that returns station_id, parameter, reference_timestamp, value, and a new column showing the 
-- average value for that station+parameter combination across all time (i.e., AVG(value) OVER (PARTITION BY 
-- station_id, parameter)), alongside each individual row's actual value. Limit it to station BEH's tre200d0 
-- parameter with TOP 10, so you can visually see individual values sitting next to the constant partition 
-- average.

SELECT TOP 10 station_id, parameter, reference_timestamp, value,
       AVG(value) OVER (PARTITION BY station_id, parameter) AS average_value
FROM [lf-ogd-smn_d_recent]
WHERE station_abbr = 'BEH' AND parameter = 'tre200d0'

-- modify your query to add ORDER BY reference_timestamp inside the OVER(...) clause (alongside the existing 
-- PARTITION BY), keeping everything else the same. Run it and compare: does average_value now change from row 
-- to row, rather than staying constant?

SELECT TOP 10 station_id, parameter, reference_timestamp, value,
       AVG(value) OVER (PARTITION BY station_id, parameter ORDER BY reference_timestamp) AS average_value
FROM [lf-ogd-smn_d_recent]
WHERE station_abbr = 'BEH' AND parameter = 'tre200d0'

-- write a query that, for a single date (pick one from your data) and a single parameter (e.g., tre200d0), 
-- ranks all stations by value in descending order using RANK(), returning station_abbr, value, and the rank.

SELECT station_abbr, value, 
        RANK() OVER (ORDER BY value DESC) AS rank
FROM [lf-ogd-smn_d_recent]
WHERE reference_timestamp = '2026-01-01 00:00:00.000' AND parameter = 'tre200d0'
