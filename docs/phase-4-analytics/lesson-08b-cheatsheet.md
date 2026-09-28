# Lesson 8b Cheatsheet: Monthly Fact Table & Scaling Tradeoffs

## Fact Constellation

Multiple fact tables at different grains, sharing dimensions where they apply.

| | Daily fact | Monthly fact |
|---|---|---|
| Table | `[lf-ogd-smn_d]` | `[lf-ogd-smn_m]` |
| Time dimension | `dim_date` (`date_id` = YYYYMMDD) | `dim_month` (`month_id` = YYYYMM) |
| Shared | `dim_stations`, `dim_parameters` | `dim_stations`, `dim_parameters` |

Don't mix grains in one table. A row's meaning would be ambiguous.

## Month Dimension

```python
seasons = ['Winter', 'Spring', 'Summer', 'Fall']
dti = pd.date_range('1975-01-01', '2026-12-31', freq='MS')   # 'MS' = month START ('M' = month end)

row = [dt, dt.year, dt.month, dt.month_name(),
       seasons[dt.month % 12 // 3],
       dt.year*10**2 + dt.month]                              # YYYYMM
```

## Creating a Fact Table With Constraints Upfront

```sql
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'lf-ogd-smn_m')
BEGIN
CREATE TABLE [lf-ogd-smn_m] (
    full_month_date DATETIME NOT NULL,
    station_abbr CHAR(3) NOT NULL,
    parameter VARCHAR(255) NOT NULL,
    value FLOAT,                       -- nullable: real missing measurements exist
    station_id INT NOT NULL,
    parameter_id INT NOT NULL,
    month_id INT NOT NULL,
    PRIMARY KEY (station_id, parameter_id, month_id),
    FOREIGN KEY (station_id) REFERENCES [dim_stations](station_id),
    FOREIGN KEY (parameter_id) REFERENCES [dim_parameters](parameter_id),
    FOREIGN KEY (month_id) REFERENCES [dim_month](month_id)
)
END
```
A table auto-created by a Spark write has no `NOT NULL`, PK or FKs, so all of it has to be added afterwards. Creating the table first avoids that.

## Sizing a Load Before Running It

- Estimate rows: stations × periods × parameters (long format).
- Compare against a known reference point (rows that approached the limit before).
- Check `df.count()` right after the unpivot, before any write.
- If it's very large, chunk it (by year) and verify each chunk.

```sql
-- Table size in MB
SELECT SUM(reserved_page_count) * 8.0 / 1024 AS size_mb FROM sys.dm_db_partition_stats;
```

## Chunked Load Pattern (Databricks)

```python
from pyspark.sql.functions import year

TARGET_YEAR = 2000                      # change each run
df_year = df_long_dim.filter(year(df_long_dim.reference_timestamp) == TARGET_YEAR)   # joined DataFrame, not df_long
print(df_year.count())                  # compare with the count in SQL afterwards
# then write with mode("append"), numPartitions=1, batchsize=10000
```
```sql
SELECT COUNT(*) FROM [table] WHERE YEAR(reference_timestamp) = 2000;   -- verify each year
```

## Write Throughput and Tier Scaling

| Observation | Meaning |
|---|---|
| `numPartitions` 1 → 4 made the load slower | Consistent with a log-rate cap, not concurrency |
| 100 DTU cut ~28 min to ~3.5 min per year | The tier was the bottleneck |

- Temporary scale-up: change DTUs in the portal, load, then scale back. **Azure SQL never scales down on its own.** Set a reminder.
- The portal shows a monthly figure for continuous use. Divide by ~730 for the hourly rate.
- **The max storage size is a separate setting** from the DTU slider. Scaling up alone doesn't raise it.
- Before planning to scale back down, check that the final data size fits the lower tier (Basic: 2 GB).
- Database size is much larger than the source CSVs (row expansion when unpivoting, indexes, transaction log).

## Deleting a Lot of Rows

```sql
DELETE FROM [table] WHERE YEAR(reference_timestamp) = 2000;   -- one year at a time
```
- A single huge `DELETE` can time out. Batch it and verify each batch (`SELECT COUNT(*) ... = 0`).
- `DELETE` doesn't reduce the file size. Reclaiming space needs a shrink (`DBCC SHRINKDATABASE`), which can run long, fragments indexes, and is better run from a client other than the portal's Query Editor.
- Do large deletes and shrinks while still on the higher tier.

## Primary Key of a Table

```sql
SELECT kc.name AS constraint_name, c.name AS column_name, ic.key_ordinal
FROM sys.key_constraints kc
JOIN sys.index_columns ic ON kc.parent_object_id = ic.object_id AND kc.unique_index_id = ic.index_id
JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE kc.parent_object_id = OBJECT_ID('table-name') AND kc.type = 'PK'
ORDER BY ic.key_ordinal;
```

## Power BI: Adding a Second Fact Table

- Only add the new tables. Re-adding tables already in the model creates duplicate queries (`name (2)`), which can cause a cyclic reference error.
- Check relationships after import. They may not be auto-detected. Create them by dragging key to key.
- A dimension can be `*:1`, single-direction, to two fact tables at once.
- Sort a text column properly: select `month_name` → **Sort by column** → `month`.

## DAX: `CALCULATE` With a Boolean Filter

```
Historical Average = CALCULATE(AVERAGE('lf-ogd-smn_m'[value]), 'dim_month'[year] < YEAR(TODAY()))
```
- A Boolean filter on a column **replaces** any existing filter on that column from the visual. With `year` on a chart axis, every point may show the same value.
- Use `YEAR(TODAY())` instead of a hardcoded year so the measure doesn't need editing every year.
- Test a new `CALCULATE` measure in a matrix by the filtered column before building the chart.

## Mermaid ER Direction

In `erDiagram`, put the **dimension** on the left of `||--o{` (one dimension row to many fact rows):
```
DIM_STATIONS ||--o{ FACT : station_id
```