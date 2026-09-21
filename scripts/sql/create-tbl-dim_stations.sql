IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_stations')
BEGIN
CREATE TABLE [dim_stations] (
station_abbr VARCHAR(255) UNIQUE NOT NULL,
station_name VARCHAR(255),
station_canton VARCHAR(255),
station_wigos_id VARCHAR(255),
station_type_en VARCHAR(255),
station_dataowner VARCHAR(255),
station_data_since DATETIME,
station_height_masl FLOAT,
station_height_barometer_masl FLOAT,
station_coordinates_wgs84_lat FLOAT,
station_coordinates_wgs84_lon FLOAT,
station_exposition_en VARCHAR(255),
station_url_en VARCHAR(255),
station_id INT IDENTITY(1,1) PRIMARY KEY
)
END