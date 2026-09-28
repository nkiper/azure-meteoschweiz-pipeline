# Lesson 8 Cheatsheet: Power BI Semantic Models

## Power BI on Mac

| | Power BI Service (web) | Power BI Desktop |
|---|---|---|
| OS | Any (browser) | Windows only |
| Connect to new data sources | ❌ | ✅ |
| Build semantic models | ❌ | ✅ |
| Full DAX | Limited | ✅ |
| On Mac | Native | Via Parallels (Microsoft-authorized on Apple Silicon) |

## Import vs. DirectQuery

| | Import | DirectQuery |
|---|---|---|
| Speed after load | Instant (in-memory) | Live query every interaction |
| Freshness | As of last refresh | Always current |
| Source load | None after refresh | Every interaction hits the source |
| Best fit here | ✅ — daily update cadence, Basic-tier constraints | Would add load to an already-constrained DB |

⚠️ Scheduled automatic refresh requires **publishing to Power BI Service** — Desktop alone only refreshes manually.

## Relationships

- Power BI Import can auto-detect relationships from DB foreign keys — check anyway via **Manage Relationships**
- Star schema default: `*:1` (many fact rows to one dimension row), **single**-direction cross-filter (dimension → fact)

## Calculated Column vs. Measure

- Measure (dynamic, filter-context-aware, nothing stored)
Average Value = AVERAGE('fact_table'[value])
- Aggregations (`AVERAGE`, `SUM`, `COUNT`) → measures, not calculated columns
- A measure's home table = whichever table was selected at creation time — movable afterward, doesn't affect calculation

## `COUNT` vs. `COUNTROWS`

Datapoint Count = COUNT('fact_table'[value]) -- non-blank values only
Total Row Count = COUNTROWS('fact_table') -- every row, regardless of nulls

The gap between these two = a real data-quality signal (rows that exist structurally vs. rows with an actual value).

## Long-Format Data: Naive Aggregation Trap

If `value`'s meaning depends on another column (e.g. `parameter`), an unfiltered `AVERAGE(value)` mixes incompatible units. Either:
- Rely on report-level filtering (slicer/grouping) — flexible, but only correct when the filter is actually applied, or
- Hard-code parameter-specific measures with `CALCULATE(..., table[param_col] = "x")` — safe, but doesn't scale to many parameters

## Diagnosing a Data Anomaly (workflow used this lesson)

1. Spot an unexpected pattern via a measure in a matrix visual (e.g., row counts varying by group)
2. Narrow the hypothesis (missing entirely vs. shorter range vs. scattered gaps) with a cross-tab
3. Go to the **raw source file** directly to confirm whether the anomaly is in the source data or introduced by the pipeline
4. For scattered/internal gaps specifically, compare actual row count against the full expected date range (`end - start`) to detect gaps that a start/end-date check alone would miss