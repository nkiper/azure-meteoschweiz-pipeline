# Lesson 5 Cheatsheet: Azure Databricks

## Databricks CLI Quick Reference

```bash
# Authenticate (use workspace ROOT URL, not JDBC/ODBC path!)
databricks configure
# host: https://adb-<id>.<n>.azuredatabricks.net

# Verify auth
databricks current-user me

# Secret scopes
databricks secrets create-scope <scope-name>
databricks secrets put-secret <scope> <key>     # opens editor — never pass value as a CLI arg
```

**PAT scope gotcha**: token scope ("Other APIs" vs "BI tools") restricts what you can do. Changes to scope can take up to ~10 min to propagate — don't assume a retry failure means the scope choice was wrong.

## Secret Scope Reference (Notebook Usage)

```python
dbutils.secrets.get(scope="meteoschweiz", key="adls-account-key")
```

## Serverless Compute: What's Different From a Classic Cluster

| Pattern | Classic cluster | Serverless (Spark Connect) |
|---|---|---|
| Global storage auth | `spark.conf.set("fs.azure...", key)` works | **Blocked** — use per-call `.options(**dict)` |
| SQL write | `.write.jdbc(url, table, mode, properties)` works | **Blocked** (`UNSUPPORTED_DATA_SOURCE_WRITE`) — use named format e.g. `.write.format("sqlserver")` |
| Available write options | Full JDBC driver option set | Limited, connector-specific subset — check Databricks' "Serverless write options for bundled connectors" docs |

## ADLS Access — Per-Call Options Pattern (Serverless)

```python
storage_options = {
    "fs.azure.account.key.<account>.dfs.core.windows.net":
        dbutils.secrets.get(scope="meteoschweiz", key="adls-account-key")
}

df = spark.read.format("csv") \
    .option("header", "true") \
    .option("sep", ";") \
    .option("inferSchema", "true") \
    .options(**storage_options) \
    .load("abfss://<container>@<account>.dfs.core.windows.net/raw")

df.write.format("parquet") \
    .mode("overwrite") \
    .options(**storage_options) \
    .save("abfss://<container>@<account>.dfs.core.windows.net/processed")
```

## SQL Server Write (Serverless) — Confirmed Working Pattern

```python
df.write.format("sqlserver") \
    .option("host", "<server>.database.windows.net") \
    .option("database", "<db-name>") \
    .option("dbtable", "[table-name]") \
    .option("user", dbutils.secrets.get(scope="...", key="sql-username")) \
    .option("password", dbutils.secrets.get(scope="...", key="sql-password")) \
    .option("batchsize", 10000) \
    .option("numPartitions", 1) \
    .mode("overwrite") \
    .save()
```

**Full documented option list** (serverless `sqlserver` connector): `host`, `port`, `database`, `connectionTimeout`, `encrypt`, `trustServerCertificate`, `user`, `password`, `authentication`, `dbtable`, `batchsize`, `numPartitions`, `queryTimeout`, `isolationLevel`, `truncate`.

## Timestamp Parsing (PySpark)

```python
from pyspark.sql.functions import to_timestamp
df = df.withColumn("reference_timestamp",
                    to_timestamp(df["reference_timestamp"], "dd.MM.yyyy HH:mm"))
```
⚠️ Spark format letters ≠ Python `strftime`: `MM` = month, `mm` = minutes. Mismatches silently produce `null`, not an error.

## Wide → Long Reshape

```python
value_columns = [c for c in df.columns if c not in ('station_abbr', 'reference_timestamp')]

df_long = df.unpivot(
    ids=['station_abbr', 'reference_timestamp'],
    values=value_columns,                 # pass explicitly — 'values' was required on Spark 4.2.0 despite docs
    variableColumnName='parameter',
    valueColumnName='value'
)
```

**Sanity check**: `df_long.count()` should equal `len(value_columns) * df.count()`.

## Diagnosing a Stalled SQL Write — Checklist

1. Does the target table exist? `SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '...'`
2. Is the row count changing over time? `SELECT COUNT(*) FROM [table]` (repeat every 1-2 min)
   — ⚠️ can stay at 0 the whole time if the write is one uncommitted transaction; not proof of a stall by itself
3. What's actually executing?
```sql
   SELECT r.session_id, r.status, r.wait_type, r.wait_time, t.text
   FROM sys.dm_exec_requests r
   CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
   WHERE r.database_id = DB_ID('<db-name>')
```
4. Multiple sessions, same INSERT text, `wait_type = PAGELATCH_EX` → **last-page insert contention** (parallel writers fighting over the same physical page). Fix: reduce `numPartitions`.
5. Single session, `status = runnable`/`running`, `wait_type = NULL` → healthy, just slow. Let it run, monitor periodically.

## Azure Databricks Cost Notes

- Workspace creation: free. Billing starts only when a **cluster runs**.
- **Standard tier retired** — Premium (with 14-day DBU trial) is the only option as of this writing.
- Trial covers DBU cost; **VM compute may be billed separately** — verify before assuming $0.
- Pricing page's default monthly figures assume 24/7 operation (730 hrs) — actual cost for short, auto-terminated sessions is a tiny fraction of that.
- VM family **quota** can block cluster creation entirely ("Estimated available: 0") — check Subscriptions → Usage + quotas by region/VM family; not a configuration bug.
- **Terminate vs. delete**: terminating a cluster stops billing and preserves config for restart; deleting the whole workspace removes everything. Terminate between sessions, don't delete the workspace.
- Set a **budget alert** (Cost Management + Billing → Budgets) before running any usage-billed resource for the first time.

## Naming Conventions Added This Lesson

| Resource | Name | Notes |
|---|---|---|
| Databricks workspace | `dbw-nkipermeteo-dev` | `dbw-` is the more standard/recognizable prefix vs. `dbs-` |
| Secret scope | `meteoschweiz` | No enforced convention from Databricks; kept consistent with project naming |
| Long-format table | `[lf-ogd-smn_d_recent]` | Hyphenated → requires bracket escaping, same as `[ogd-smn_d_recent]` |