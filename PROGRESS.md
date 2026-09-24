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

### Lesson 6a: Data Warehouse Schema Design
- **Status**: Completed
- **Topics**:
  - Star schema fundamentals: fact vs. dimension tables, surrogate keys vs. natural keys, why surrogate keys exist (identity insulation, not primarily performance)
  - Designing and loading `dim_stations`, `dim_parameters` (English-only filtering, reused local Python/pyodbc pattern — no ADLS/Databricks needed for small static files)
  - SQL Server-specific syntax: `IDENTITY(1,1)`, multi-table `UPDATE ... FROM ... JOIN`, `GO` batch separation for DDL+DML, `NOT NULL` prerequisites for primary keys
  - Backfilling foreign keys onto an existing 1.6M-row fact table (add columns → populate via UPDATE/JOIN → verify → enforce NOT NULL → add PK)
  - Diagnosing `LOG_RATE_GOVERNOR` (Azure SQL's transaction-log throttling) as a third recurring instance of Basic tier's compute/throughput ceiling
  - Redesigning the Databricks notebook from full `overwrite` to incremental `append` (max-timestamp filter + proper Spark `.join()` for surrogate keys, replacing an inefficient per-row loop draft)
  - Databricks Git folders: connecting a notebook to GitHub, diagnosing a `.gitignore` `*.ipynb` rule blocking change detection
- **Key Deliverables**:
  - `dim_stations` (158 rows), `dim_parameters` (181 rows) — surrogate + natural keys, `UNIQUE NOT NULL` constraints
  - `scripts/setup/generate_dim_stations_schema.py`, `load_dim_stations.py`
  - `scripts/setup/generate_dim_parameters_schema.py`, `load_dim_parameters.py`
  - `[lf-ogd-smn_d_recent]`: `station_id`/`parameter_id` foreign keys, composite `PRIMARY KEY (station_id, reference_timestamp, parameter_id)`
  - Revised Databricks notebook (`scripts/databricks/`, Git-tracked) — incremental append pattern, verified end-to-end (61,698 new rows, zero duplicates, zero NULL FKs)
  - `ARCHITECTURE.md` updated to reflect full star schema
  - `docs/phase-3-warehouse/lesson-06a-summary.md`, `lesson-06a-cheatsheet.md`
- **Date Completed**: September 21, 2026

### Lesson 6b: Advanced SQL — JOINs, CTEs, Window Functions
- **Status**: Completed
- **Topics**:
  - JOINs (2-table, 3-table) across fact and dimension tables; column-qualification rule; inner vs. left join equality guarantees
  - CTEs for structuring multi-step queries
  - `GROUP BY` rule for functionally-dependent joined columns
  - Window functions: `PARTITION BY`, partition-wide vs. running aggregates (`ORDER BY` inside `OVER`), default window frame
  - Ranking functions (`ROW_NUMBER`, `RANK`, `DENSE_RANK`) and their tie-handling differences, confirmed against real ties in the data
- **Key Deliverables**:
  - Practice queries: multi-table joins with `dim_stations`/`dim_parameters`, a CTE (`high_elevation_stations`), running averages, station ranking by value with observed ties
  - `docs/phase-3-warehouse/lesson-06b-summary.md`, `lesson-06b-cheatsheet.md`
- **Date Completed**: September 21, 2026

### Lesson 7: Date Dimension & Schema Documentation
- **Status**: Completed
- **Topics**:
  - Generated (not sourced) dimension table design — `dim_date` built programmatically, no external file
  - Surrogate key convention specific to date dimensions (`YYYYMMDD` integer) vs. `IDENTITY`, and why a real `DATE`/`DATETIME` column is still needed alongside it
  - Deliberately excluding `date_id` from the fact table's composite primary key (granularity/future-proofing reasoning)
  - Casting to `DATE` before joining/comparing `DATETIME` values, to avoid silent time-component mismatches
  - PySpark join `on=` column-resolution rules, learned through direct testing (select-then-drop pattern for join-only columns)
  - Reused the Lesson 6a backfill/constraint sequence a third time; caught and fixed missing `FK_lf_station`/`FK_lf_parameter` constraints on the live table
  - Formally retiring legacy artifacts: table rename (`sp_rename`), file rename (`git mv`) + deprecation comments, deliberately leaving historical docs unedited
  - Consolidated schema documentation via a Mermaid ER diagram in `ARCHITECTURE.md`
- **Key Deliverables**:
  - `dim_date` (365 rows): `date_id`, `full_date`, `year`, `month`, `month_name`, `season`
  - `scripts/setup/generate_dim_date_schema.py`, `load_dim_date.py`
  - `[lf-ogd-smn_d_recent]`: `date_id` FK added/backfilled; `FK_lf_station`/`FK_lf_parameter` re-verified and re-added
  - Databricks notebook: three-dimension join in the incremental-load flow, verified (18,486 new rows, zero duplicates, zero NULL FKs)
  - `[legacy_ogd-smn_d_recent]`, `legacy_generate_wide_fact_schema.py`, `legacy_load_wide_fact_data.py`
  - `ARCHITECTURE.md`: Mermaid star schema diagram
  - `docs/phase-3-warehouse/lesson-07-summary.md`, `lesson-07-cheatsheet.md`
- **Date Completed**: September 24, 2026

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