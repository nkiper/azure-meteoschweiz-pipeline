# Lesson 5: Azure Databricks Data Processing

## Overview

This lesson closed a gap between the project's designed architecture and what had actually been built: ADLS Gen2 had been provisioned in Lesson 2 but never used. Lesson 5 wired it into the pipeline properly, introduced Databricks as the transformation layer, and reshaped the wide-format weather data into a long/tidy format suitable for analytical modeling (Power BI cubes, later lessons).

## Corrected Pipeline

MeteoSchweiz API

↓ (download_meteoschweiz_data.py)

Local CSVs

↓ (upload_to_adls.py — NEW)

Azure Data Lake Storage Gen2 (raw/)

↓ (Databricks notebook: reshape wide → long)

├─→ ADLS Gen2 (processed/) — Parquet, overwrite each run

└─→ Azure SQL Database — new table [lf-ogd-smn_d_recent], overwrite each run

↓

Power BI


**Existing wide-format table** `[ogd-smn_d_recent]` (Lesson 4) is retained as-is, fed by the original local `load_data.py`/MERGE path. The new long-format table `[lf-ogd-smn_d_recent]` is fed exclusively by the Databricks notebook.

## Concepts Learned

### Why the architecture gap existed
`load_data.py` (Lesson 3/4) went straight from local disk to Azure SQL via `pyodbc`, bypassing ADLS entirely — despite `ARCHITECTURE.md` specifying ADLS as the landing zone. Caught and fixed in this lesson.

### ADLS Gen2 upload from Python
- `azure-storage-file-datalake` SDK: `DataLakeServiceClient` → `FileSystemClient` → `DataLakeDirectoryClient`/`DataLakeFileClient`
- Access-key auth (via `.env`), consistent with the project's established "simple first" pattern
- `create_file_system()` raises `ResourceExistsError` on a duplicate container — needs explicit handling
- `create_directory()` was observed to be idempotent by default (no error on duplicate) — inconsistent with `create_file_system()`'s behavior; worth remembering this asymmetry
- Local per-station folder structure flattened when uploaded, since filenames already encode station abbreviation

### Databricks workspace & cluster
- **Standard pricing tier has been retired**; Premium (with a 14-day free-DBU trial) is now the only option
- Trial covers DBU cost; underlying VM compute billed separately 
- Workspace creation itself is free; billing starts only when a cluster runs
- VM core **quota** can block cluster creation ("Estimated available: 0") on trial/low-tier subscriptions — resolved by finding an available VM family (`Standard_D4pds_v6`) via the quota page, not by fixing configuration
- Auto-termination (10 min) is essential to control cost on a resource billed per-minute-while-running, unlike SQL Basic tier's flat pricing
- Databricks CLI required for secret scope management — authenticated via PAT, using **workspace root URL** (not the JDBC/ODBC HTTP path, which is a different value and caused an early auth bug)
- PAT scope choice ("Other APIs" vs "BI tools") is enforced — narrower scopes block specific operations (e.g., `clusters list` required broader scope than `current-user me`); scope changes can take up to ~10 minutes to propagate

### Databricks Secrets
- Storage account key, SQL username, and SQL password all stored in a Databricks-backed secret scope (`meteoschweiz`), avoiding plaintext credentials in notebook code
- `databricks secrets create-scope <name>` / `databricks secrets put-secret <scope> <key>` (opens an editor for the value — avoids shell history exposure)
- Referenced in notebooks via `dbutils.secrets.get(scope=..., key=...)`

### Serverless compute quirks (Spark Connect)
This was the dominant technical theme of the lesson — several behaviors specific to Databricks' serverless compute model, distinct from a traditional cluster:
- **Global `spark.conf.set(...)` for storage auth is blocked** on serverless Spark Connect. Fix: pass credentials per-call via an `.options(**storage_options)` dict on each read/write instead of setting them once globally.
- **Generic `.write.jdbc(...)` is not allowed** on serverless compute (`UNSUPPORTED_DATA_SOURCE_WRITE`) — only a specific allow-list of named data source formats (including `sqlserver`) can run DML.
- The named `sqlserver` format has its **own, more limited option set**, documented separately at Databricks' "Serverless write options for bundled connectors" page — distinct from the generic JDBC writer's `properties` dict pattern.

### Reading multiple files & schema inference
- `spark.read.csv()` reads an entire directory (158 files) into one DataFrame in a single call — no manual looping needed, unlike the pandas-based Lesson 3/4 scripts
- `inferSchema=True` needed to get numeric columns as `double` rather than `string` (Spark's default)
- Custom date formats (`dd.MM.yyyy HH:mm`) are not auto-detected by `inferSchema` — required explicit `to_timestamp(col, "dd.MM.yyyy HH:mm")`, same underlying issue as `pd.to_datetime(..., format=...)` in Lesson 3
- Spark's format-pattern letters differ subtly from Python's `strftime` codes (`MM` = month vs `mm` = minutes) — a common silent-null source if mismatched

### Wide-to-long reshape
- `DataFrame.unpivot(ids=[...], values=[...], variableColumnName=..., valueColumnName=...)`
- On this environment's Spark version (4.2.0), `values` was required despite official docs describing it as optional — resolved by passing it explicitly via a list comprehension over `df.columns`, avoiding hand-typing ~40 column names
- Row-count sanity check after reshape: `(number of value columns) × (original row count)` should match the unpivoted row count — useful validation step

### Diagnosing a stalled/slow SQL write
A genuinely valuable diagnostic sequence, worth remembering as a general pattern for "write appears stuck":
1. Check whether the target table exists (confirms DDL succeeded)
2. Check `SELECT COUNT(*)` on the target table repeatedly over time (confirms whether rows are landing — though note this can show 0 the entire time if the write is in one uncommitted transaction)
3. Query `sys.dm_exec_requests` (joined with `sys.dm_exec_sql_text`) to see exactly what SQL is actively executing against the database, its `status`, and `wait_type`
4. `wait_type = PAGELATCH_EX` across multiple concurrent sessions writing to the same table indicates **last-page insert contention** — multiple parallel writers fighting over the same physical data page, not a genuine hang
5. Root cause traced to: 8 parallel Spark tasks (`numPartitions` implicitly matching partition count) each issuing single-row inserts concurrently against the same table

### Fix: `batchsize` and `numPartitions`
- Both are options for the serverless `sqlserver` connector (confirmed via Databricks' official docs)
- `numPartitions=1` eliminated the `PAGELATCH_EX` contention entirely (only one writer session observed afterward) — trading write parallelism for correctness/stability
- `batchsize=10000` set alongside it; actual effectiveness inconclusive (single-row INSERT text in `sys.dm_exec_requests` doesn't necessarily disprove batching at the protocol level)
- Final write: ~1.55M rows, single partition, took **28 minutes**

## Design Decision: Overwrite vs. Staging + MERGE

**Originally planned**: staging table + `MERGE` (same idempotency pattern as Lesson 4), to support incremental upserts as new data arrives.

**What was actually built**: direct `mode="overwrite"` into `[lf-ogd-smn_d_recent]`.

**Reasoning for accepting this simplification**:
- The `sqlserver` serverless connector's write path proved difficult to get performant even for a single overwrite; adding a staging table would mean debugging the same connector twice
- At current data volume (~1.55M rows, 28 min), a full reload on each run is an acceptable, simpler idempotency strategy — the table is always fully replaced, so no duplicate-row risk, just different tradeoffs (full rewrite cost vs. incremental merge complexity)
- Time already invested in connector troubleshooting made this the pragmatic stopping point for this lesson

## What We Built

- `scripts/setup/upload_to_adls.py` — uploads local raw CSVs to ADLS `raw/` (flattened), access-key auth via `.env`
- Databricks workspace `dbw-nkipermeteo-dev` (Premium trial), cluster: single-node, `Standard_D4pds_v6`, Runtime 17.3 LTS, no Photon, 10-min auto-termination
- Databricks secret scope `meteoschweiz` with `adls-account-key`, `sql-username`, `sql-password`
- Databricks notebook: reads all 158 raw CSVs from ADLS → infers schema → parses timestamps → unpivots wide to long → writes Parquet to ADLS `processed/` → overwrites `[lf-ogd-smn_d_recent]` in Azure SQL
- New table `[lf-ogd-smn_d_recent]`: `station_abbr`, `reference_timestamp`, `parameter`, `value` — ~1.55M rows

## Next Steps

- Advanced SQL (JOINs, CTEs, window functions) — Lesson 6, introduced just-in-time for warehouse/analytics work
- Power BI: building the semantic model/cube on top of `[lf-ogd-smn_d_recent]`