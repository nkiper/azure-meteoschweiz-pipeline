IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_parameters')
BEGIN
CREATE TABLE [dim_parameters] (
parameter_shortname VARCHAR(255) UNIQUE NOT NULL,
parameter_description_en VARCHAR(255),
parameter_group_en VARCHAR(255),
parameter_granularity VARCHAR(255),
parameter_decimals INT,
parameter_datatype VARCHAR(255),
parameter_unit VARCHAR(255),
parameter_id INT IDENTITY(1,1) PRIMARY KEY
)
END