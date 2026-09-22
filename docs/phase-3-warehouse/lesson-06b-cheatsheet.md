# Lesson 6b Cheatsheet: JOINs, CTEs, Window Functions

## JOIN

```sql
SELECT b.station_name, a.reference_timestamp, a.value
FROM [lf-ogd-smn_d_recent] a
JOIN [dim_stations] b ON a.station_id = b.station_id
WHERE b.station_abbr = 'BEH'
```
- Always qualify columns (`a.col`, `b.col`) once 2+ tables are involved
- Chain more `JOIN ... ON ...` clauses for 3+ tables
- Inner join guarantees join-key equality only for matched rows — doesn't hold the same way across a `LEFT JOIN`'s unmatched rows

## CTE

```sql
WITH cte_name AS (
    SELECT col1, col2 FROM some_table WHERE condition
)
SELECT ...
FROM cte_name
JOIN other_table ON ...
```

## GROUP BY Rule

Every non-aggregated `SELECT` column must be in `GROUP BY` or wrapped in an aggregate — **even functionally-dependent columns from a joined table**:

```sql
-- Fails: c.parameter_unit not in GROUP BY or aggregated
SELECT b.parameter, AVG(b.value), c.parameter_unit
FROM t b JOIN dim_parameters c ON b.parameter_id = c.parameter_id
GROUP BY b.parameter

-- Fix (preferred when 1:1 with the group):
GROUP BY b.parameter, c.parameter_unit
```

## Window Functions

```sql
-- Partition-wide aggregate (same value every row in the partition)
AVG(value) OVER (PARTITION BY station_id, parameter) AS avg_all_time

-- Running/cumulative aggregate (value changes row to row)
AVG(value) OVER (PARTITION BY station_id, parameter ORDER BY reference_timestamp) AS running_avg
```
- `PARTITION BY` with no rows outside a single group (e.g. already filtered by `WHERE`) = no-op, safe to omit
- Brackets `[...]` in explanatory text mean "optional" — never literal SQL syntax; don't copy them into a query

## Ranking Functions

```sql
SELECT station_abbr, value,
       RANK() OVER (ORDER BY value DESC) AS rnk
FROM [lf-ogd-smn_d_recent]
WHERE reference_timestamp = '...' AND parameter = 'tre200d0'
```

| Function | Tie behavior |
|---|---|
| `ROW_NUMBER()` | Unique per row, ignores ties |
| `RANK()` | Ties share rank, **skips** next value(s) |
| `DENSE_RANK()` | Ties share rank, **no skip** |