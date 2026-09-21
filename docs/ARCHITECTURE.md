Resource group: rg-meteoschweiz-dev
Region: Switzerland North (data residency + geographic proximity)

MeteoSchweiz API 

    ↓ (download_data.py)

Local CSVs 

    ↓ (upload step)

Azure Data Lake Storage Gen2 (raw/)

    ↓ (Databricks notebook)

Databricks

    ↓ (Databricks: read, reshape to long format,  upsert)

    ├─→ Azure Data Lake Storage Gen2 (processed/)  [long-format Parquet]

    └─→ Azure SQL Database (long-format table, append mode (filter via last timestamp in db))

                ↓

            Power BI

## Components

- **Azure Data Lake Storage Gen2**: Stores raw CSV files in hierarchical structure
- **Azure Databricks**: Python-based data processing and transformation
- **Azure SQL Database**: OLAP data warehouse for analytical queries
- **Power BI**: Visualization and dashboard layer