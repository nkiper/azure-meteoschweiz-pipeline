# Lesson 6a Cheatsheet: Data Warehouse Schema Design

## Star Schema Quick Reference

| | Fact table | Dimension table |
|---|---|---|
| Size | Large | Small(er) |
| Content | Mostly numeric, measurements/events | Descriptive attributes |
| Keys | Foreign keys to dimensions | Own surrogate primary key + natural key |
| Example | `[lf-ogd-smn_d_recent]` | `dim_stations`, `dim_parameters` |

**Surrogate key**: auto-incrementing integer PK, decoupled from the natural/business key. Insulates against natural-key reuse/renaming and enables historical tracking (slowly changing dimensions) — not primarily a performance play.

## SQL Server Syntax Gotchas (new this lesson)

```sql
-- Auto-increment: SQL Server, NOT MySQL syntax
station_id INT IDENTITY(1,1) PRIMARY KEY

-- Multi-table UPDATE: SQL Server style
UPDATE fact
SET fact.station_id = dim.station_id
FROM [lf-ogd-smn_d_recent] fact
JOIN [dim_stations] dim ON fact.station_abbr = dim.station_abbr;
-- NOT: UPDATE fact JOIN dim ON ... SET ... (MySQL style — invalid here)
```

**DDL + DML in one batch**: separate with `GO`, or run as two executions —
```sql
ALTER TABLE t ADD new_col INT;
GO
UPDATE t SET new_col = ...;   -- fails with "Invalid column name" if in same batch, no GO
```

**Adding a PRIMARY KEY on existing data — required sequence**:
```sql
ALTER TABLE t ADD CONSTRAINT ck UNIQUE (col);         -- optional, for natural keys
ALTER TABLE t ALTER COLUMN col1 INT NOT NULL;          -- required for EVERY key column
ALTER TABLE t ALTER COLUMN col2 DATETIME NOT NULL;      -- even ones you're sure are never null
GO
ALTER TABLE t ADD CONSTRAINT pk PRIMARY KEY (col1, col2);
```
⚠️ Auto-generated schemas (e.g. from Spark writes) rarely set `NOT NULL` by default — check every intended key column's nullability with:
```sql
SELECT COLUMN_NAME, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 't'
```

## Diagnosing Slow/Stuck Operations — Extended Checklist

(Builds on Lesson 5's checklist — add this new wait type)

| Wait type | Meaning | Fix |
|---|---|---|
| `PAGELATCH_EX` | Multiple writers contending for the same physical page | Reduce concurrency (e.g. `numPartitions`) |
| `LCK_M_S` | Waiting on a shared lock (often a background client query) | Usually harmless/transient — check it clears |
| `LOG_RATE_GOVERNOR` | Azure SQL throttling transaction log write rate — tier-based hard cap | No fix by waiting; only a higher service tier removes the cap |

Cross-check any `sys.dm_exec_requests` finding against Azure SQL **Metrics** (CPU %, DTU %) for independent confirmation.

## Databricks Notebook: Incremental Load Pattern

```python
# 1. Read dimensions
dim_stations = spark.read.format("sqlserver")...load()
dim_parameters = spark.read.format("sqlserver")...load()

# 2. Join surrogate keys (proper Spark join — NOT a Python loop over dimension rows)
df_long_dim = (df_long
    .join(dim_stations.select("station_abbr", "station_id"), on="station_abbr", how="left")
    .join(dim_parameters.select(dim_parameters.parameter_shortname.alias("parameter"), "parameter_id"),
          on="parameter", how="left")
)

# 3. Get current max timestamp — pushed down to SQL Server, not pulled into Spark
max_ts_df = (spark.read.format("sqlserver")
    .option("dbtable", "(SELECT MAX(reference_timestamp) AS max_ts FROM [lf-ogd-smn_d_recent]) AS sub")
    ...load())
max_ts = max_ts_df.collect()[0][0]

# 4. Filter to new rows only
df_new = df_long_dim.filter(df_long_dim.reference_timestamp > max_ts)

# 5. Append (safe — filter guarantees no duplicates)
df_new.write.format("sqlserver")...mode("append").save()
```

⚠️ Don't populate lookup values with a Python `for` loop calling `.withColumn()` per dimension row — that builds a huge chained execution plan. Use `.join()`.

## Databricks Git Folders

- Connect a workspace folder to a GitHub repo for in-UI commit/push (no local export needed)
- Check `.gitignore` for accidental blanket rules (e.g. `*.ipynb`) that silently prevent notebooks from being tracked as changed
- Notebook formats: "source" (plain `.py`/`.sql`/etc, code only) vs "ipynb" (includes outputs)