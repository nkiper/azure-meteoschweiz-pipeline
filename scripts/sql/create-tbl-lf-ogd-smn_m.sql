IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'lf-ogd-smn_m')
BEGIN
CREATE TABLE [lf-ogd-smn_m] (
    full_month_date DATETIME NOT NULL,
    station_abbr CHAR(3) NOT NULL,
    parameter VARCHAR(255) NOT NULL,
    value FLOAT,
    station_id int NOT NULL,
    parameter_id int NOT NULL,
    month_id int NOT NULL,
    PRIMARY KEY (station_id, parameter_id, month_id),
    FOREIGN KEY (station_id) REFERENCES [dim_stations](station_id),
    FOREIGN KEY (parameter_id) REFERENCES [dim_parameters](parameter_id),
    FOREIGN KEY (month_id) REFERENCES [dim_month](month_id)
)
END