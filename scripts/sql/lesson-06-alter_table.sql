ALTER TABLE [lf-ogd-smn_d_recent] ADD station_id INT, parameter_id INT;
GO

UPDATE fact
SET fact.station_id = dim.station_id
FROM [lf-ogd-smn_d_recent] fact
JOIN [dim_stations] dim ON fact.station_abbr = dim.station_abbr;

UPDATE fact
SET fact.parameter_id = dim.parameter_id
FROM [lf-ogd-smn_d_recent] fact
JOIN [dim_parameters] dim ON fact.parameter = dim.parameter_shortname;

SELECT COUNT(*) FROM [lf-ogd-smn_d_recent] WHERE station_id IS NULL OR parameter_id IS NULL;

ALTER TABLE [lf-ogd-smn_d_recent]
ADD CONSTRAINT FK_lf_station FOREIGN KEY (station_id) REFERENCES [dim_stations](station_id);

ALTER TABLE [lf-ogd-smn_d_recent]
ADD CONSTRAINT FK_lf_parameter FOREIGN KEY (parameter_id) REFERENCES [dim_parameters](parameter_id);

ALTER TABLE [lf-ogd-smn_d_recent] ALTER COLUMN station_id INT NOT NULL;
ALTER TABLE [lf-ogd-smn_d_recent] ALTER COLUMN parameter_id INT NOT NULL;
ALTER TABLE [lf-ogd-smn_d_recent] ALTER COLUMN reference_timestamp DATETIME NOT NULL;

ALTER TABLE [lf-ogd-smn_d_recent]
ADD CONSTRAINT PK_lf_fact PRIMARY KEY (station_id, reference_timestamp, parameter_id);

SELECT COLUMN_NAME, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'lf-ogd-smn_d_recent'
AND COLUMN_NAME IN ('station_id', 'parameter_id', 'reference_timestamp')

SELECT kc.name AS constraint_name, c.name AS column_name
FROM sys.key_constraints kc
JOIN sys.index_columns ic ON kc.parent_object_id = ic.object_id AND kc.unique_index_id = ic.index_id
JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE kc.parent_object_id = OBJECT_ID('lf-ogd-smn_d_recent') AND kc.type = 'PK'