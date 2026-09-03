Resource group: rg-meteoschweiz-dev
Region: Switzerland North (data residency + geographic proximity)

Raw Data (MeteoSchweiz) 
    ↓
Azure Data Lake Storage Gen2
    ↓
Azure Databricks
    ↓
Azure SQL Database
    ↓
Power BI

## Components

- **Azure Data Lake Storage Gen2**: Stores raw CSV files in hierarchical structure
- **Azure Databricks**: Python-based data processing and transformation
- **Azure SQL Database**: OLAP data warehouse for analytical queries
- **Power BI**: Visualization and dashboard layer