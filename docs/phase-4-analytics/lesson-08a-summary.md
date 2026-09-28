# Lesson 8: Power BI Semantic Models

## Overview

This lesson connected Power BI to the completed star schema, built the relationships that turn four separate imported tables into an actual queryable model, wrote the first DAX measures, and used those measures to investigate and root-cause two real data anomalies in the underlying dataset.

## Concepts Learned

### Tabular model, not "cube"
Modern Power BI does not build a traditional multidimensional OLAP cube (unlike legacy SQL Server Analysis Services) — it builds a **tabular semantic model**. The OLAP-style slicing/dicing/aggregation experience is preserved, but the underlying engine and terminology have moved on; worth knowing this when reading Power BI's own documentation, which consistently uses "tabular model," not "cube."

### Power BI Desktop vs. Power BI Service
- **Desktop**: Windows-only, no native Mac version (confirmed via Microsoft's own docs — a declined feature request). Required for the actual authoring work this lesson needed: connecting to new data sources, Power Query transformations, building semantic models, full DAX.
- **Service** (app.powerbi.com, browser-based): works on any OS, but explicitly does **not** support connecting to new data sources or building semantic models — sufficient only for viewing/sharing already-built reports.
- Resolved by running Desktop inside **Parallels** (Microsoft-authorized for Windows on Apple Silicon) — the correct tool for this specific need, not overkill, given the Service's genuine capability gap.

### Import vs. DirectQuery
- **DirectQuery**: live queries sent to Azure SQL on every interaction — no staleness, but real query load on the source every time
- **Import**: data copied into Power BI's in-memory engine at refresh time — instant interaction afterward, but requires a refresh (scheduled or manual) to stay current
- **Decision**: Import — matches the project's daily update cadence, and avoids adding interactive query load to a Basic-tier database already shown (Lessons 4/5/6a) to have real throughput/compute constraints
- **Known limitation, accepted deliberately**: scheduled automatic refresh requires publishing to Power BI Service (a Desktop-only setup doesn't support it) — for this learning project, refresh is manual, meaning both the Databricks pipeline *and* the Power BI refresh depend on being manually triggered. Accepted as reasonable for a non-production learning project, but explicitly noted rather than left as a silent gap.

### Relationships
- Power BI's Import connector auto-detected all three fact-to-dimension relationships from the database's actual foreign key metadata (`station_id`, `parameter_id`, `date_id`) — correct columns, correct *:1 cardinality, single-direction cross-filtering, with no manual correction needed
- Worth knowing this isn't guaranteed in general — auto-detection can occasionally mismatch on ambiguous column names; verifying via "Manage Relationships" is still worth doing rather than trusting it blindly
- Single-direction (dimension → fact) filtering is the conventional, safer default for a plain star schema; bidirectional filtering risks ambiguous filter paths, especially with multiple dimensions

### Calculated column vs. measure
- **Calculated column**: computed per row, physically stored
- **Measure**: computed dynamically in response to the current filter context (slicers, visual groupings) — nothing stored
- Aggregations like "average value" are inherently cross-row concepts and belong as measures, not calculated columns
- A measure's "home table" is set by whichever table was selected when it was created — not automatically inferred from the columns its formula references; can be moved afterward without affecting how it calculates

### Long-format data and naive aggregation
The fact table's long format means `value`'s unit/meaning depends on `parameter` — a flat, unfiltered `AVERAGE(value)` mixes incompatible units (temperature with precipitation, etc.) and is meaningless. Resolved by keeping the measure generic (`AVERAGE(value)`) and relying on report-level filtering (a parameter slicer/grouping) to give it meaning — a deliberate flexibility-over-safety tradeoff, since the alternative (one hard-coded measure per parameter) doesn't scale to ~40 parameters and isn't yet known which ones Lesson 9's dashboards will need.

### `COUNT` vs. `COUNTROWS`
- `COUNT(column)` counts non-blank values in that specific column
- `COUNTROWS(table)` counts all rows regardless of any column's content
- These can differ meaningfully when a table has real `NULL`s in the counted column — as it does here (confirmed: some parameter/station/day combinations have a row but no actual measurement, consistent with the null-handling built into `load_data.py` back in Lesson 3)
- The difference between the two is itself a useful data-quality signal (rows that exist structurally vs. rows with an actual value) — kept as two separate, clearly-named measures rather than collapsed into one

## Data Quality Investigation

Using the new measures (`Total Row Count` by station × parameter in a matrix), found two stations with fewer rows than the rest (266):
- **BLA**: 127 rows — data begins May 2026. Traced to the May 28, 2025 landslide/glacier collapse at Blatten; the station's earlier historical data ends around that event, consistent with equipment damage and a later restart.
- **NAS**: 255 rows — spans the full date range (Jan 1–Sep 23) but has an **11-day gap, May 4–14, 2026**, confirmed by direct inspection of the raw source CSV (not a pipeline artifact — the gap exists in MeteoSchweiz's own published data). Likely cause not confirmed (plausibly a station outage), but the gap itself is fully traced to source, not to any step in this project's pipeline.

Both findings confirm the pipeline is faithfully reproducing source data, including its real gaps — a genuinely useful validation of the whole pipeline built across Lessons 3–7, not just a Power BI exercise.

## What We Built

- Power BI Desktop (via Parallels) connected to Azure SQL (`sqls-nkipermeteo-dev`/`db-nkipermeteo`), Import mode, SQL authentication
- Four tables imported: fact (`lf-ogd-smn_d_recent`) + three dimensions (`dim_stations`, `dim_parameters`, `dim_date`) — legacy table deliberately excluded
- Three relationships (auto-detected, verified correct): fact → each dimension, *:1, single-direction
- Three DAX measures on the fact table: `Average Value`, `Datapoint Count` (`COUNT(value)`), `Total Row Count` (`COUNTROWS(...)`)
- A station × parameter matrix investigation that traced two real data anomalies to their source

## Next Steps

- Lesson 9: Dashboard & Report Design — building actual visuals, likely introducing parameter-specific measures as needed per dashboard, and deciding whether the gap/data-quality findings from this lesson deserve their own dashboard element