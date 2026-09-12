# Lesson 4: Multi-Station Data Ingestion

## Overview

This lesson scaled the pipeline from a single station to all 158 SwissMetNet stations: automating downloads via the MeteoSchweiz API, redesigning the schema around a unified table, and building an idempotent loading process using SQL Server's MERGE statement.

## Concepts Learned

### Data Modeling at Scale
- **Fact table pattern**: A single unified table (rather than one table per entity) is the standard approach when entities share identical structure — enables cross-entity queries and matches the pattern needed for BI tools downstream
- **Schema vs. data lifecycle**: Schema creation is a one-time operation; data loading is repeated — these should be separate scripts, not bundled together
- **Verifying assumptions before modeling**: Checked column consistency across all 158 stations' CSVs (in both directions — extra and missing columns) before committing to a single schema

### Idempotent Data Loading
- **MERGE statement**: T-SQL's native upsert — matches incoming rows against existing ones by key, only inserting when no match is found
- **Why not plain INSERT**: A pipeline that re-runs (e.g., to pick up new data over time) needs to avoid creating duplicate rows; MERGE handles this without needing separate check-then-insert logic
- **`IF NOT EXISTS` guards**: Wrapping CREATE TABLE so schema scripts are safe to re-run without erroring or destroying existing data

### SQL Syntax Details
- **Identifiers vs. string literals**: `[brackets]` quote identifiers (table/column names); `'single quotes'` denote string values — using the wrong one produces confusing errors (e.g., "Invalid column name" when a table name was meant)
- **Statement splitting**: Executing multiple statements from one `.sql` file via pyodbc requires manually splitting on `;`, filtering out empty strings from trailing/missing semicolons

### Python Debugging Patterns
- **Silent vs. loud bugs**: A script that runs without error can still produce wrong output — string slicing errors and dtype mismatches don't raise exceptions, but produce incorrect table names or column types
- **Truthiness vs. equality**: `if some_string:` checks `bool(some_string)`, not `some_string == True` — a non-empty string is truthy but never equal to `True`
- **Bare `except:` clauses**: Swallow the real error message, making it hard to diagnose failures across 158 stations — switched to `except Exception as e:` to surface actual causes

### Performance Diagnosis
- **Execution plans**: `Clustered Index Seek` (efficient) vs. `Scan` (reads much of the table) — confirmed the MERGE's row-matching was using an efficient seek via the primary key's clustered index
- **Azure SQL metrics**: Blended `DTU percentage` can look moderate while a single resource (CPU, Data IO, or Log IO) is maxed — checking them individually pinpointed CPU as the bottleneck, not indexing or I/O
- **Basic tier limitations**: Very little compute headroom (5 DTU); row-by-row MERGE execution across 158 stations was enough to sustain 100% CPU

## What We Built

**Unified table:** `[ogd-smn_d_recent]`

**Schema:**
- Composite primary key: (station_abbr, reference_timestamp)
- 39 columns total (station ID + 38 measurement parameters)
- Wrapped in `IF NOT EXISTS` for safe re-running
- Replaces the per-station table design from Lesson 3

**Data loaded:** Daily measurements for all 158 SwissMetNet stations, via MERGE-based upsert

## Scripts Created

**1. `scripts/setup/download_meteoschweiz_data.py`**
- Reads station abbreviations from `ogd-smn_meta_stations.csv`
- Downloads each station's daily CSV via the MeteoSchweiz API
- Saves to `data/raw/<station_abbr>/` folders

**2. `generate_schema.py` (updated)**
- Now generates one schema for a unified table instead of per-station tables
- Wraps CREATE TABLE in `IF NOT EXISTS ... BEGIN ... END`
- Table name derived from granularity/keyword rather than station abbreviation, to support other granularities later

**3. `run_sql_script.py`**
- Generic helper to execute any `.sql` file via pyodbc
- Splits file contents on `;`, filters empty statements, commits after execution
- Kept separate from data loading so schema updates don't depend on the loading pipeline

**4. `load_data.py` (updated)**
- Loops through all 158 stations from the metadata CSV
- Uses a MERGE statement (built dynamically from column names) instead of INSERT, for safe re-runs
- Shares a single pyodbc connection across all stations, with per-station error handling so one failure doesn't abort the run

## Key Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| `station_abbr` and `reference_timestamp` dtypes assumed rather than verified | Printed `df[col].dtype` directly to confirm before hardcoding the type lookup |
| `WHERE name = [ogd-smn_d_recent]` failed with "Invalid column name" | Used string literal (`'...'`) instead of bracket-quoted identifier |
| Re-running schema script would error on existing table | Wrapped CREATE TABLE in `IF NOT EXISTS` |
| Re-running data load would create duplicate rows | Switched from INSERT to MERGE, keyed on the composite primary key |
| `.split(';')` on the SQL file could leave empty strings, causing execute errors | Filtered with `if SQL_string.strip():` before executing |
| Bare `except:` hid the real error during multi-station loading | Changed to `except Exception as e:` to surface actual failure causes |
| Loading all 158 stations row-by-row was CPU-bound on the Basic tier (confirmed via Azure Metrics) | Diagnosed via execution plan (seek, not scan) and individual metrics (CPU maxed, IO low); accepted the tradeoff rather than optimizing immediately |

## Result

All 158 stations loaded successfully via `load_data.py`. Verified with:
```sql
SELECT COUNT(DISTINCT station_abbr) AS station_count, COUNT(*) AS total_rows
FROM [ogd-smn_d_recent];
```

## Next Steps

- Revisit performance if needed: batched MERGE (multi-row VALUES source), `fast_executemany`, or scaling the tier temporarily
- Move to the Databricks transformation layer
- Begin Power BI dashboard development