Dataset: Automatic weather stations - Measurement values

# Description

SwissMetNet, the automatic monitoring network of MeteoSwiss, comprises 158 automatic monitoring stations. The data set contains current measurements for each station on temperature, precipitation, wind, pressure, snow, humidity, sunshine duration, and radiation in 10 minutes ('t'), hourly ('h'), daily ('d'), monthly ('m') and yearly ('y') resolutions. There are updated data sets since midnight ('now'), from the current year up to yesterday ('recent') and since the beginning of the measurement in ten-year increments ('historical'). 

# Details

| Property         |                                                                             |
| ---------------- | --------------------------------------------------------------------------- |
| Data format      | .csv                                                                        |
| Volume           | 158 stations, 15 files per station, filesize?                               |
| Granularity      | 10 minutes ('t'), hourly ('h'), daily ('d'), monthly ('m') and yearly ('y') |
| Access Method    | API, manual download                                                        |
| Update Frequency | Continual                                                                   |
| Provided by      | Federal Office of Meteorology and Climatology MeteoSwiss                    |
| Identifier       | 35323752-ed32-4cc1-8a75-898c749b777b                                        |

# Structure

## top-level

ogd-smn_meta_datainventory.csv: List with columns station_abbr, meas_cat_nr, data_since, data_till, owner

ogd-smn_meta_parameters.csv:    List of all measurement parameters. Columns (prefix: param_): shortname, description_de, "_fr, "_it, "_en, group_de, "_fr, "_it, "_en, granularity, decimals, datatype, unit

ogd-smn_meta_stations.csv:      List of measurement stations. Columns (prefix: station_): abbr, name, canton, wigos_id, type_de, "_fr, "_it, "_en, dataowner, data_since, height_masl, height_barometer_masl, coordinates_lv95_east, coordinates_lv95_north, coordinates_wgs84_lat, coordinates_wgs84_lon, exposition_de, "_fr, "_it, "_en, url_de, "_fr, "_it, "_en

## data files

For each station, there are 15 files, named with ogd-smn_[station_abbr]\_[granularity]_[keyword].
granularity takes the values: 10 minutes ('t'), hourly ('h'), daily ('d'), monthly ('m') and yearly ('y')
keyword takes the values: historical, historical_[year]-[year], recent, now

# Link to data

https://data.geo.admin.ch/browser/index.html#/collections/ch.meteoschweiz.ogd-smn?.language=en