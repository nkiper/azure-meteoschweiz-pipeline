# Lesson 7: Date Dimension & Schema Documentation

## Overview

This lesson completed the star schema begun in Lesson 6a by adding a third dimension (`dim_date`), formally retiring the superseded wide-format fact table, and producing a single consolidated schema diagram — closing out the warehouse-design phase of the project.

## Concepts Learned

### Generated (not sourced) dimension tables
Unlike `dim_stations`/`dim_parameters` (loaded from MeteoSchweiz metadata CSVs), `dim_date` has no external source file — it's fully derivable from a date range. Schema was hand-written rather than run through the CSV-inference pattern, since the columns and types were fully known upfront; row generation was done in Python via `pandas.date_range`, computing `year`, `month`, `month_name`, `season` (meteorological convention), and a `YYYYMMDD`-integer surrogate key per date.

### Date dimension design decisions
- **Surrogate key as `YYYYMMDD` integer** (e.g., `20260315`) rather than an arbitrary `IDENTITY` sequence — human-readable and naturally sortable, a common convention specific to date dimensions
- **A real `DATETIME`/`DATE` column (`full_date`) kept alongside the integer key** — the integer alone isn't sufficient for native date arithmetic, range filtering, or joining against a `DATETIME`-typed fact column; both serve different purposes (key vs. actual date operations)
- **`date_id` deliberately excluded from the fact table's primary key** — since `date_id` represents only the date portion of `reference_timestamp`, including it in the PK would create a uniqueness constraint that breaks the moment finer-than-daily granularity (e.g., hourly data) is ever ingested into the same table; `reference_timestamp` alone already provides real per-row uniqueness

### Joining on cast dates, not raw timestamps
`dim_date.full_date` and `[lf-ogd-smn_d_recent].reference_timestamp` are both `DATETIME`, but direct equality risks silent mismatches from any time-component discrepancy (fractional seconds, rounding). Both the SQL backfill and the Databricks notebook join explicitly cast both sides to `DATE` before comparing (`CAST(... AS DATE)` in SQL; `.cast("date")` in PySpark) — deliberately avoiding another instance of the silent-format-mismatch class of bug already seen twice earlier in the project (ADLS DNS, Spark timestamp parsing).

### PySpark join-condition column resolution
Extending the notebook's incremental-load join to a third dimension surfaced a genuine PySpark subtlety, resolved through direct testing rather than assumption:
- A column referenced in a join's `on=` condition must exist in the actual DataFrame being joined at that point — referencing a column from a *different* (even related) DataFrame object raises `Cannot resolve dataframe column`, even when the two DataFrames share underlying lineage
- Fix: include the cast/aliased column in the `.select(...)` being joined (so it's resolvable in the `on=` condition), then `.drop(...)` it afterward once no longer needed
- `on=` for a join needs an explicit equality expression between two column objects (e.g., `col("day") == df.reference_timestamp.cast("date")`) when the two sides don't already share a literal column name — a plain string on one side of `==` does not produce a valid join condition

### Backfill/constraint sequence (reused a third time)
Same pattern as Lesson 6a's two dimensions, applied again for `date_id`: `ALTER TABLE ADD` (nullable) → `UPDATE ... FROM ... JOIN` (with the date-cast condition) → verify zero NULLs → `ALTER COLUMN ... NOT NULL` → `ADD CONSTRAINT FOREIGN KEY`. Also caught and fixed a real gap during this: `FK_lf_station`/`FK_lf_parameter` were found missing from the live table (data was intact; constraints simply hadn't been present) and were re-added safely.

### Legacy artifact management
- `[ogd-smn_d_recent]` (Lesson 4's wide-format table, fully superseded by the star schema) renamed to `[legacy_ogd-smn_d_recent]` via `sp_rename`, making its deprecated status visible directly in the database schema rather than only in documentation
- `generate_schema.py`/`load_data.py` (the Lesson 3 scripts that built and loaded the original wide table) renamed via `git mv` to `legacy_generate_wide_fact_schema.py`/`legacy_load_wide_fact_data.py` — combining a status prefix with a more descriptive name than the originals had, plus an in-file deprecation comment
- Historical lesson docs (Lesson 3, Lesson 4, Lesson 5) deliberately left unedited — they correctly describe what existed at the time; only currently-active references were checked/updated

### Consolidated schema documentation
Added a Mermaid `erDiagram` to `ARCHITECTURE.md` — GitHub-renderable, version-controlled as plain text, showing the fact table and all three dimensions with their key relationships. Composite primary key (`station_id, reference_timestamp, parameter_id`) marked across all three contributing columns, with a prose note clarifying they form one joint key rather than three independent ones (a real limitation of Mermaid's ER notation, worked around rather than left ambiguous).

## What We Built

- `dim_date` (365 rows, current year): `date_id` (PK, `YYYYMMDD` int), `full_date`, `year`, `month`, `month_name`, `season`
- `scripts/setup/generate_dim_date_schema.py`, `load_dim_date.py`
- `[lf-ogd-smn_d_recent]`: `date_id` foreign key added and backfilled; also re-confirmed/re-added `FK_lf_station`/`FK_lf_parameter`, which were found missing
- Databricks notebook: third dimension join added to the incremental-load flow, verified end-to-end (18,486 new rows in the first run with all three dimensions wired in — no duplicates, no NULL FKs)
- `[legacy_ogd-smn_d_recent]` (renamed from `[ogd-smn_d_recent]`), `legacy_generate_wide_fact_schema.py`, `legacy_load_wide_fact_data.py` — formally marked deprecated
- `ARCHITECTURE.md`: consolidated Mermaid star schema diagram

## Next Steps

- Phase 4: Power BI — semantic model/cube on top of the completed star schema, then dashboards and reports