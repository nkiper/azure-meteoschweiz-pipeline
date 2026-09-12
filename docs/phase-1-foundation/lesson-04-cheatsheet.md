# Lesson 4 Cheatsheet: Multi-Station Data Ingestion

## Quick Reference

### Idempotent Schema Creation Pattern
```sql
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'table_name')
BEGIN
CREATE TABLE [table_name] (
    column1 DATATYPE NOT NULL,
    column2 DATATYPE,
    PRIMARY KEY (column1, column2)
)
END
```
Safe to re-run without erroring or destroying existing data.

### MERGE Statement (Idempotent Upsert)
```sql
MERGE INTO [target_table] AS target
USING (SELECT ? AS col1, ? AS col2) AS source
ON target.col1 = source.col1 AND target.col2 = source.col2
WHEN NOT MATCHED THEN
    INSERT (col1, col2)
    VALUES (source.col1, source.col2);
```
Only inserts if no matching row exists — replaces INSERT for pipelines that need to re-run without duplicating data.

### Identifiers vs. String Literals

[brackets]      -- quoted identifier (table/column name)
'single quotes' -- string literal (a value)


```sql
WHERE name = 'my_table'    -- correct: comparing a string
WHERE name = [my_table]    -- wrong: looks for a COLUMN named my_table
```

### Multi-Statement SQL Files via pyodbc
```python
with open(SQL_FILE, 'r') as f:
    SQL_strings = f.read().replace('\n', ' ')

for SQL_string in SQL_strings.split(';'):
    if SQL_string.strip():       # skip empty strings from trailing/missing ;
        cursor.execute(SQL_string)

connection.commit()
```

### Python Truthiness Quick Reference

bool('')            -- False (empty string)
bool('text')         -- True (non-empty string)
bool([])             -- False (empty list)
'text' == True       -- False (string is never equal to a bool)
if some_string:       -- checks bool(some_string), NOT == True


### Exception Handling: Bare vs. Specific
```python
# BAD: hides the real error
try:
    risky_call()
except:
    print("Something failed")

# GOOD: surfaces the actual cause
try:
    risky_call()
except Exception as e:
    print(f"Something failed: {e}")
```

### Checking pandas dtypes Before Mapping to SQL
```python
print(df['column'].dtype)   # confirm actual dtype string first
```
Don't assume `object` vs `str` vs `datetime64[ns]` vs `datetime64[us]` — this varies by pandas version and platform.

### Diagnosing Query Performance
```sql
-- Enable in your SQL tool: "Include Actual Execution Plan"
-- Or:
SET SHOWPLAN_TEXT ON;
```

| Plan operator | Meaning |
|---|---|
| Clustered Index Seek | Efficient — near-constant-time lookup |
| Clustered/Table Scan | Reads much/all of the table — investigate |

Requires literal values, not `?` placeholders — substitute real values or test a simplified equivalent query.

### Diagnosing Azure SQL Bottlenecks
Don't rely on blended `DTU percentage` alone — check individually in Azure Portal → Metrics:

| Metric | High value indicates |
|---|---|
| `cpu_percent` | Compute-bound (many small statement executions) |
| `log_io_percent` | Write-heavy, many small committed transactions |
| `data_io_percent` | Heavy data page reads/writes (e.g. index fragmentation) |

Basic tier (5 DTU) has very little headroom — expect limits under sustained batch loads.

### Fact Table vs. Per-Entity Tables
Before creating one table per entity (per station, per region, etc.), check whether entities share identical structure:
```python
# Verify column consistency across all files before committing to a schema
all_columns = set(first_df.columns)
for file in other_files:
    df = pd.read_csv(file)
    assert set(df.columns) == all_columns
```
If structure matches, prefer one unified table with the entity as part of the primary key — better for cross-entity queries and BI tools.

### File Structure

scripts/

├── setup/

│ ├── download_meteoschweiz_data.py (API → data/raw/<station>/)

│ ├── generate_schema.py (CSV → idempotent CREATE TABLE)

│ ├── run_sql_script.py (generic .sql file executor)

│ └── load_data.py (loops all stations → MERGE upsert)

└── sql/

└── create-tbl-ogd-smn_d_recent.sql


data/

├── raw/

│ └── <station_abbr>/ogd-smn_<station_abbr>_d_recent.csv

├── processed/

docs/

├── ogd-smn_meta_stations.csv

├── lesson-04-summary.md

└── lesson-04-cheatsheet.md


### Running the Full Load
```bash
python scripts/setup/run_sql_script.py   # create/verify schema (once)
python scripts/setup/load_data.py        # load all 158 stations (repeatable)
```

### Verifying the Load
```sql
SELECT COUNT(DISTINCT station_abbr) AS station_count, COUNT(*) AS total_rows
FROM [ogd-smn_d_recent];
```