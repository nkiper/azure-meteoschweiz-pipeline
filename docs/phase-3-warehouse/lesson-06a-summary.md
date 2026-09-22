# Lesson 6a: Data Warehouse Schema Design

## Overview

This part of Lesson 6 closed the gap between having raw fact data (`[lf-ogd-smn_d_recent]`, built in Lesson 5) and having an actual **star schema** — introducing dimension tables, surrogate keys, referential integrity, and an incremental (non-full-reload) load pattern.

## Concepts Learned

### Star schema fundamentals
- **Fact table**: large, mostly numeric, references dimensions via foreign keys — `[lf-ogd-smn_d_recent]`
- **Dimension table**: smaller, descriptive, answers "who/what/where" — `dim_stations`, `dim_parameters`
- **Surrogate keys**: auto-incrementing integer primary keys (`station_id`, `parameter_id`), distinct from natural business keys (`station_abbr`, `parameter_shortname`)
  - Primary rationale: insulation from natural-key history/identity issues (a code being renamed or reused for a different real-world entity) and support for tracking changes over time ("slowly changing dimensions") — not primarily a performance optimization, though smaller-key joins are a secondary benefit
  - Natural keys retained as `UNIQUE NOT NULL` columns in the dimension tables, both for verification and as a data-integrity safeguard (prevents accidental duplicate loads of the same real-world entity)

### Dimension table design
- `dim_stations`: built from `ogd-smn_meta_stations.csv`, filtered to English-only descriptive columns (dropped `_de`/`_fr`/`_it` variants) and dropped the LV95 coordinate system (kept WGS84 for future mapping/Power BI use)
- `dim_parameters`: built from `ogd-smn_meta_parameters.csv`, same English-only filtering; retained `granularity` as a deliberate choice
- Both loaded via adapted versions of the Lesson 3 `generate_schema.py`/`load_data.py` pattern — reused directly from local Python/pyodbc, **not** routed through ADLS/Databricks, since these are small, static, single local files with no transformation-at-scale need
- `dim_parameters` intentionally contains more rows (181) than the fact table currently uses (~39–40) — it holds MeteoSchweiz's full published parameter catalog across all granularities, not just the daily subset currently ingested; a legitimate star-schema situation, not a bug

### SQL Server-specific syntax encountered
- `IDENTITY(1,1)` for auto-incrementing surrogate keys — **not** `AUTO_INCREMENT` (MySQL syntax)
- `UPDATE ... SET ... FROM ... JOIN ...` — SQL Server's multi-table UPDATE syntax, structurally different from `UPDATE ... JOIN ...` (MySQL/standard-SQL style)
- DDL (`ALTER TABLE ADD`) run in the same batch as DML referencing the new column can fail with "Invalid column name" — needs a `GO` batch separator, or must be run as two separate executions
- `ALTER TABLE ... ADD CONSTRAINT ... PRIMARY KEY` fails with "Cannot define PRIMARY KEY constraint on nullable column" unless every key column is explicitly `NOT NULL` — even when the actual data contains zero NULLs, the column-level nullability metadata must say so
- Auto-generated schemas (e.g., from Spark's `.write.format("sqlserver")`) do **not** infer `NOT NULL` — every column, including ones that are never actually null in practice (like `reference_timestamp`), needs explicit `ALTER COLUMN ... NOT NULL` before it can participate in a primary key

### Backfilling foreign keys onto an existing large table
Sequence used (and why it matters):
1. `ALTER TABLE ADD station_id INT, parameter_id INT` (nullable at first)
2. `UPDATE ... FROM ... JOIN` against each dimension table, populating the new columns from natural-key matches
3. Verify zero NULLs remain before proceeding
4. `ALTER COLUMN ... NOT NULL` on all three key columns (including `reference_timestamp`, which needed it despite never actually containing NULLs)
5. `ADD CONSTRAINT ... PRIMARY KEY` last, once all three columns are provably non-nullable

### Diagnosing `LOG_RATE_GOVERNOR`
A new wait type, distinct from the `PAGELATCH_EX` contention seen in Lesson 5:
- Azure SQL enforces a **transaction log write-rate cap** proportional to service tier — Basic tier's cap is low
- `LOG_RATE_GOVERNOR` means the session is being deliberately throttled by the platform, not stuck or blocked by another session
- Confirmed via Azure SQL Metrics showing sustained CPU (~20%) alongside the wait — a genuinely different bottleneck category than pure CPU-bound work
- No amount of waiting speeds this up; it's a fixed rate ceiling, not variable contention — the only lever is a higher service tier
- **Running theme across the whole project**: Basic tier's compute/throughput ceiling has now been the direct cause of slow operations three separate times (Lesson 4's local MERGE, Lesson 5's Spark connector writes, this ALTER COLUMN validation) — worth treating as an accepted, standing project tradeoff rather than re-solving each time it recurs

### Redesigning the Databricks notebook: from full overwrite to incremental append
Original Lesson 5 design (`mode="overwrite"` on every run) directly conflicted with preserving manually-added schema (foreign keys, primary key) — every re-run would have dropped and recreated the table.

**Revised notebook flow**:
1. Read `dim_stations`/`dim_parameters` into Spark (`spark.read.format("sqlserver")`)
2. Join surrogate keys onto `df_long` via `.join(...)` (not a per-row Python loop — an early draft mistakenly built 339 sequential `.withColumn()` calls in a loop over dimension rows, which would have been a serious performance problem at 1.55M rows; corrected to a proper Spark `.join()`)
3. Query the fact table's current `MAX(reference_timestamp)` — pushed down to SQL Server via a subquery in `dbtable` (`(SELECT MAX(...) AS max_ts FROM ...) AS alias`) rather than pulling the whole table into Spark just to aggregate one value
4. Filter `df_long_dim` to only rows newer than that max
5. Write with `mode="append"` instead of `overwrite` — safe specifically because the filter guarantees no pre-existing rows are being re-sent

Verified end-to-end with a real incremental run: 61,698 new rows added cleanly, zero duplicates, zero NULL foreign keys.

### Databricks Git integration
- Databricks **Git folders** connect a workspace folder directly to a GitHub repo for in-UI commit/push — notebook placed at `scripts/databricks/`, consistent with the project's organize-by-artifact-type convention
- Notebooks can be tracked in "source" or "ipynb" format — worth knowing this distinction exists if sync behavior seems off
- Root cause of "notebook not detected as changed" in this project: a leftover `*.ipynb` blanket rule in `.gitignore` (removed once no longer needed)

## What We Built

- `dim_stations` (158 rows): surrogate key `station_id`, natural key `station_abbr` (`UNIQUE NOT NULL`), English-only descriptive columns, WGS84 coordinates only
- `dim_parameters` (181 rows): surrogate key `parameter_id`, natural key `parameter_shortname` (`UNIQUE NOT NULL`), English-only descriptive columns, includes `granularity`
- `scripts/setup/generate_dim_stations_schema.py`, `scripts/setup/load_dim_stations.py`
- `scripts/setup/generate_dim_parameters_schema.py`, `scripts/setup/load_dim_parameters.py`
- `[lf-ogd-smn_d_recent]`: now has `station_id`/`parameter_id` foreign keys (backfilled + enforced via `FOREIGN KEY` constraints), composite `PRIMARY KEY (station_id, reference_timestamp, parameter_id)`
- Revised Databricks notebook (`scripts/databricks/`, Git-tracked): incremental filter + surrogate-key join + append, replacing Lesson 5's full-overwrite design
- `ARCHITECTURE.md` updated to reflect the full star schema and incremental-load design

## Next Steps

- Lesson 6b: JOINs, CTEs, window functions (querying the schema built here)
- Lesson 7: further star schema work / additional dimensions if needed, per revised roadmap