# Learning Progress - Azure MeteoSchweiz Pipeline

## Phase 1: Foundation (In Progress)

### Lesson 1: Azure Fundamentals & Account Setup
- **Status**: Completed
- **Topics**: Resource hierarchy, Azure Portal navigation, architecture planning
- **Key Deliverable**: `docs/ARCHITECTURE.md`
- **Date Completed**: 3. 9. 2026

### Lesson 2: Azure Data Lake Storage Gen2 Setup
- **Status**: Completed
- **Topics**: Storage Accounts, Data Lake vs Blob, access control, redundancy
- **Key Deliverable**: Storage Account `nkipermeteo` with container `data` and folder structure
- **Date Completed**: 4. 9. 2026

### Lesson 3: SQL Fundamentals
- **Status**: Completed
- **Topics**: 
  - Azure SQL Database setup and configuration
  - Relational schema design (primary keys, constraints, data types)
  - SQL basics and OLAP vs OLTP
  - Python-to-SQL integration (pyodbc)
  - Secure credential management (.env, parameterized queries)
  - ODBC driver setup and troubleshooting
  - SELECT, WHERE, ORDER BY, GROUP BY queries
- **Key Deliverables**:
  - Azure SQL Server: `sqls-nkipermeteo-dev`
  - Database: `db-nkipermeteo`
  - Table: `[ogd-smn_beh_d_recent]` (41 columns, composite primary key)
  - `scripts/setup/generate_schema.py` (auto-generates CREATE TABLE from CSV)
  - `scripts/setup/load_data.py` (loads CSV data into SQL via pyodbc)
  - `scripts/sql/lesson-04-exploration.sql` (exploratory queries)
  - `requirements.txt` updated with pandas, pyodbc, python-dotenv
  - Data loaded: 246 rows of meteorological data (BEH station)
- **Date Completed**: 6. 9. 2026

### Lesson 4: Multi-Station Data Ingestion
- **Status**: Not Started
- **Topics**: 
  - Automating data download from MeteoSchweiz API
  - Loading data for all 158 stations
  - Scaling ETL pipeline
  - Handling multiple files and batch loading
- **Expected Focus**: Expand from single station (BEH) to full Swiss network

---

## Phase 2: ETL/ELT (Planned)

- Lesson 5: Azure Data Factory Pipelines
- Lesson 6: Azure Databricks Data Processing

---

## Phase 3: Data Warehouse (Planned)

- Lesson 7: Azure SQL Database Schema Design
- Lesson 8: Loading Data into DW

---

## Phase 4: Analytics & BI (Planned)

- Lesson 9: Power BI Semantic Models
- Lesson 10: Dashboard & Report Design

---

## Notes
- Data source: MeteoSchweiz automatic weather stations (158 stations)
- Portfolio repo: https://github.com/nkiper/azure-meteoschweiz-pipeline

# To do at end of project
- remember to delete 'sqls-nkipermeteo-dev'