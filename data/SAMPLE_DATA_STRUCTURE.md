# Sample data structure

Sample data file: ogd-smn_beh_d_recent.csv

Columns: A - AO (41)
Rows: 1 - 247 (incl. header)

## Column description

| index | header | description | dtype [format] |
| ----- | ------ | ----------- | ----- |
| A | station_abbr | station abbreviation (cf. ogd-smn_meta_stations.csv) | string len 3 [XXX] |
| B | reference_timestamp | measurement timestamp | timestamp [dd.mm.yyyy hh:mm] |
| C - AO | [various] | measurement parameters (cf. ogd-smn_meta_parameters.csv) | float or int |