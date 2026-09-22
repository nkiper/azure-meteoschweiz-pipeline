# Lesson 6b: Advanced SQL — JOINs, CTEs, Window Functions

## Overview

With a working star schema in place from Lesson 6a, this part covered the SQL techniques needed to actually query across it — JOINs to bring dimension context into fact queries, CTEs to structure multi-step logic readably, and window functions to compute per-row analytics without collapsing the result set.

## Concepts Learned

### JOINs
- `JOIN ... ON <fact>.<fk> = <dimension>.<pk>` connects a fact table to a dimension table via the surrogate key relationship
- **Always qualify column names with table aliases** once more than one table is involved — even when a column name is currently unambiguous, an unqualified reference becomes an error the moment two joined tables share a column name
- With an inner `JOIN`, columns that are equal by the join condition (e.g., `a.station_abbr` and `b.station_abbr` after joining on `station_id`) are guaranteed equal *for the rows in the result* — but this guarantee is specific to inner joins with fully-matched keys; a `LEFT JOIN` with unmatched rows would break that equivalence (the dimension-side column would be `NULL` even though the fact-side natural key has a real value)
- Multi-table joins (3+ tables) work by chaining additional `JOIN ... ON ...` clauses

### CTEs (Common Table Expressions)
```sql
WITH cte_name AS (
    SELECT ...
)
SELECT ...
FROM cte_name
JOIN ...
```
- A named, temporary result set defined with `WITH`, referenced like a table in the query below it
- Primarily a readability/structuring tool — equivalent to a subquery, but keeps multi-step logic legible

### `GROUP BY` rule reinforced
- Every non-aggregated column in the `SELECT` list must either be in the `GROUP BY` clause or wrapped in an aggregate function
- This applies even to columns that are *functionally dependent* on the grouping column (e.g., `parameter_unit` never actually varies within a `parameter` group) — SQL Server can't prove that in advance, so it must be either added to `GROUP BY` or wrapped in `MAX()`/`MIN()`
- **Preferred fix when the column is truly 1:1 with the group** (like `parameter` → `parameter_unit`): add it to `GROUP BY` — more honest about the relationship than wrapping it in an arbitrary aggregate
- **Appropriate when the value could genuinely vary and you want one representative value**: wrap in `MAX()`/`MIN()` instead

### Window Functions
Conceptually distinct from `GROUP BY`: **rows are not collapsed** — every original row remains, gaining an additional computed column.

```sql
AGG_FUNCTION(column) OVER (PARTITION BY grouping_col [ORDER BY sort_col]) AS new_col
```

- **`PARTITION BY`** — like `GROUP BY`, but computes within each partition without collapsing rows
- **Without `ORDER BY`** inside `OVER(...)`: aggregate computed across the *whole* partition — same value repeated on every row in that partition
- **With `ORDER BY`** inside `OVER(...)`: many functions switch to a **running/cumulative** calculation — computed over rows from the start of the partition up to and including the current row (default frame: `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`)
- `PARTITION BY` is unnecessary (a no-op) if the query's `WHERE` clause has already filtered the data down to a single logical group

### Ranking functions
All three share the same syntax (`FUNCTION() OVER (PARTITION BY ... ORDER BY ...)`), differing only in tie-handling:

| Function | Ties | Next value after a tie |
|---|---|---|
| `ROW_NUMBER()` | Ignored — every row gets a unique sequential number | Always +1 from previous |
| `RANK()` | Same rank assigned to ties | **Skips** ranks (e.g., 1, 2, 2, 4) |
| `DENSE_RANK()` | Same rank assigned to ties | **No skip** (e.g., 1, 2, 2, 3) |

## What We Practiced

- 2-table and 3-table JOINs across `[lf-ogd-smn_d_recent]`, `dim_stations`, `dim_parameters`
- A CTE (`high_elevation_stations`) filtering `dim_stations` by elevation, joined into an aggregate query over the fact table
- Running averages via `AVG(value) OVER (PARTITION BY ... ORDER BY ...)`
- Station rankings by value for a given date/parameter using `RANK()`, with real ties observed in the data confirming the skip behavior directly

## Next Steps

- Apply these techniques as needed in later warehouse/Power BI work — introduced just-in-time rather than exhaustively; more advanced window function frames (explicit `ROWS BETWEEN` clauses) or additional CTE patterns (recursive CTEs) can be picked up later if a real need arises