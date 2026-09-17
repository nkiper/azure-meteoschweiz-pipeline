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
- **Status**: Completed
- **Topics**: 
  - Automating data download from MeteoSchweiz API for all 158 stations
  - Redesigning schema: unified fact table vs. per-station tables
  - Idempotent data loading via SQL Server's MERGE statement
  - Debugging silent vs. loud bugs (string slicing, dtype mapping, truthiness)
  - Reading SQL Server execution plans (Index Seek vs. Scan)
  - Diagnosing Azure SQL performance bottlenecks (DTU, CPU%, Data IO%, Log IO%)
- **Key Deliverables**:
  - `scripts/setup/download_meteoschweiz_data.py` (downloads all 158 stations via API)
  - `scripts/setup/generate_schema.py` (updated: generates idempotent, unified-table schema)
  - `scripts/setup/run_sql_script.py` (generic .sql file executor via pyodbc)
  - `scripts/setup/load_data.py` (updated: loops all 158 stations, MERGE-based upsert)
  - `scripts/sql/create-tbl-ogd-smn_d_recent.sql` (unified table schema)
  - `docs/lesson-04-summary.md`, `docs/lesson-04-cheatsheet.md`
  - Table: `[ogd-smn_d_recent]` — unified table, 39 columns, composite primary key `(station_abbr, reference_timestamp)`
  - Data loaded: all 158 stations successfully loaded and verified (`COUNT(DISTINCT station_abbr) = 158`)
- **Known issue**: row-by-row MERGE loading is CPU-bound on the Basic tier (confirmed via execution plan + Azure metrics); accepted as a tradeoff for now — batching or scaling the tier would address it if needed later
- **Date Completed**: 11. 9. 2026

---

## Phase 2: ETL/ELT (Planned)

### Lesson 5: Azure Databricks Data Processing
- **Status**: Completed
- **Topics**:
  - Closing the ADLS Gen2 architecture gap (raw CSVs were bypassing storage entirely since Lesson 3)
  - Azure Data Lake Storage Gen2 SDK (`azure-storage-file-datalake`), access-key auth, idempotent container/directory creation
  - Azure Databricks workspace & cluster provisioning (Premium trial, quota troubleshooting, cost/auto-termination controls)
  - Databricks CLI, PAT scoping, and Databricks-backed secret scopes for credential management
  - Serverless compute (Spark Connect) constraints: blocked global `spark.conf.set`, blocked generic `.write.jdbc`, per-call `.options()` pattern, named-connector option sets
  - Reading directories of CSVs, schema inference, PySpark timestamp parsing (`to_timestamp`)
  - Wide-to-long reshaping with `DataFrame.unpivot`
  - Diagnosing a stalled SQL write via `sys.dm_exec_requests` (last-page insert contention, `PAGELATCH_EX`)
  - Tuning `batchsize`/`numPartitions` on the serverless SQL Server connector
  - Deliberate architecture simplification: full `overwrite` instead of staging + MERGE, and why
- **Key Deliverables**:
  - `scripts/setup/upload_to_adls.py` (local CSVs → ADLS `raw/`)
  - Databricks workspace `dbw-nkipermeteo-dev`, cluster (single-node, `Standard_D4pds_v6`, Runtime 17.3 LTS)
  - Secret scope `meteoschweiz` (`adls-account-key`, `sql-username`, `sql-password`)
  - Databricks notebook: ADLS `raw/` → reshape wide→long → ADLS `processed/` (Parquet) + Azure SQL
  - New table `[lf-ogd-smn_d_recent]`: long-format, ~1.55M rows (`station_abbr`, `reference_timestamp`, `parameter`, `value`)
  - `ARCHITECTURE.md` updated to reflect corrected pipeline and the overwrite-vs-MERGE decision
  - `docs/phase-2-etl/lesson-05-summary.md`, `docs/phase-2-etl/lesson-05-cheatsheet.md`
- **Date Completed**: September 17, 2026

---

## Phase 3: Data Warehouse (Planned)

- Lesson 6: Data Warehouse Schema Design & Advanced SQL
  - Star schema / dimensional modeling concepts (fact vs. dimension tables)
  - Designing dimension tables for stations and parameters (from `ogd-smn_meta_stations.csv`, `ogd-smn_meta_parameters.csv` — currently unused metadata)
  - JOINs, CTEs, window functions — introduced in service of querying the resulting schema
- Lesson 7: Building the Star Schema
  - Creating and populating `dim_stations`, `dim_parameters` (and any other dimensions identified in Lesson 6)
  - Establishing relationships to the fact table `[lf-ogd-smn_d_recent]`
  - *(Note: originally titled "Loading Transformed Data into DW" — repurposed, since Lesson 5's Databricks notebook already loads the fact table; this lesson now focuses on the dimension side)*

---

## Phase 4: Analytics & BI (Planned)

- Lesson 8: Power BI Semantic Models
- Lesson 9: Dashboard & Report Design

---

## Phase 5: Infrastructure as Code (Planned)

- Lesson 10: Terraform Fundamentals

---

## Notes
- Data source: MeteoSchweiz automatic weather stations (158 stations)
- Portfolio repo: https://github.com/nkiper/azure-meteoschweiz-pipeline

# To do at end of project
- remember to delete 'sqls-nkipermeteo-dev'