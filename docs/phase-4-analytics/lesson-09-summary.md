# Lesson 9: Dashboard & Report Design

## Overview

Building on the fact constellation from Lesson 8b, this lesson built the first real report: three visuals comparing this year's data against historical averages and monthly trends, plus a station map. Most of the lesson was working through DAX filter-context behavior and several Power BI platform quirks that don't show up until you try to combine measures from two related-but-different-grain fact tables on one visual.

## Visual 1: Historical Average by Year, with a Cross-Granularity Reference Point

A line chart of `dim_month[year]` against a historical-average measure from `[lf-ogd-smn_m]`, with a single marker showing this year's daily-table average layered on top.

### `CALCULATE` and filter context, confirmed empirically
Two measures were written for the historical/current split:
```
Historical Average = CALCULATE(AVERAGE('lf-ogd-smn_m'[value]), 'dim_month'[year] < YEAR(TODAY()))
This Year Average   = CALCULATE(AVERAGE('lf-ogd-smn_m'[value]), 'dim_month'[year] = YEAR(TODAY()))
```
With `year` already on the chart axis, a `CALCULATE` filter on that same column overrides the axis's own filter rather than combining with it — this is standard DAX behavior and was verified directly in a table visual before being trusted in the chart.

### Cross-granularity reference: parameter correspondence built into the model
The chart's second series needed this year's **daily** average (from `[lf-ogd-smn_d]`) plotted at the current year. Two problems had to be solved first, both at the model level rather than in DAX:

**1. Daily and monthly parameters use different `parameter_shortname` codes for the same measurement** (e.g. `tre200d0` vs `tre200m0` — one character differs, always in the position right before the trailing digit; not a global substitution, since other `m`/`d` characters can appear elsewhere in the same code). A standalone script (`update_dim_parameters.py`) added two nullable columns to `dim_parameters`, `corr_m_id` and `corr_d_id`, computed by transforming each row's shortname and looking up the resulting string's `parameter_id` within the same table — null where no counterpart exists. This has to be a separate, one-off script (not part of `generate_dim_parameters_schema.py`/`load_dim_parameters.py`), since it depends on `parameter_id` values that don't exist until after the initial load runs.

**2. A filter arriving through a relationship and a filter stated explicitly inside `CALCULATE` don't simply override each other the way two `CALCULATE` filters on the same table do.** The page's parameter slicer filters `dim_parameters` to the monthly parameter row; that filter propagates through the relationship into `lf-ogd-smn_d[parameter_id]` too. Adding `'lf-ogd-smn_d'[parameter_id] = CorrespondingDailyId` inside `CALCULATE` did **not** cleanly replace the relationship-propagated filter — it added a second, contradictory constraint, so nothing matched and the measure returned blank. Fixed with an explicit `REMOVEFILTERS('lf-ogd-smn_d')` before the intended condition:
```
This Year Daily Point =
VAR CurrentAxisYear = SELECTEDVALUE('dim_month'[year])
VAR CorrespondingDailyId = SELECTEDVALUE('dim_parameters'[corr_d_id])
RETURN
IF(
    CurrentAxisYear = YEAR(TODAY()),
    CALCULATE(
        AVERAGE('lf-ogd-smn_d'[value]),
        REMOVEFILTERS('lf-ogd-smn_d'),
        'dim_date'[month] = SELECTEDVALUE('dim_month'[month]),
        'lf-ogd-smn_d'[parameter_id] = CorrespondingDailyId
    )
)
```
Diagnosed by testing `SELECTEDVALUE('dim_parameters'[corr_d_id])` alone in a card first (confirmed correct), then the full measure alone in a card (blank) — isolating the fault to the `CALCULATE` filter interaction rather than the lookup itself.

### Two measures on one line chart: the Legend well restriction
Dragging a second measure into a line chart's Y-axis field kept replacing the first one rather than adding to it. Cause: a populated **Legend** field well restricts a Power BI line chart to a single Y-axis measure. Fix: remove the field from Legend; multiple measures placed directly in the Y-axis well render as separate series with their own auto-generated legend, no explicit Legend field needed.

### Dynamic title via a text-typed measure
The Y-axis title field did not offer conditional formatting (no `fx`), but the chart's overall **Title** (General section of the Format pane) did — with one condition: the bound measure must have its data type explicitly set to **Text**. A new measure combining `parameter_description_en` and `parameter_unit` was greyed out in the title's field picker until its type was changed from the default (decimal) to Text.

## Visual 2: Historical Average vs. This Year, by Month

A second chart on the same page, `dim_month[month]` (sorted by `month`) on the axis, `Historical Average` and `This Year Average` as two Y-axis values — using the same Legend-well fix as Visual 1.

### Scoping a slicer to one visual on a shared page
The page's month slicer needed to filter Visual 1 (which relies on a single selected month to resolve `This Year Daily Point`) but not Visual 2 (which needs all months on its own axis). Fixed via **Format ribbon → Edit interactions**, setting the month slicer's effect on Visual 2 to **None** while leaving it active for Visual 1 and for other slicers on both visuals.

## Visual 3: Station Map

A map visual using `dim_stations`' `coordinates_wgs84_lat`/`coordinates_wgs84_lon` (kept specifically for this purpose back in Lesson 6a, over the LV95 pair).

### Enabling map visuals
Power BI disables map visuals by default (a security setting, given they can send data to Bing/Azure Maps). Enabled via **File → Options and settings → Options → Security**, under both the file-level and Global sections — **took effect only after a full restart of Power BI Desktop**, not immediately.

### Click-driven selection and why the map's own title didn't update
Clicking a station's dot updates *other* visuals on the page correctly (confirmed with a test card showing `SELECTEDVALUE('dim_stations'[station_abbr])`, which updated on click) — but a title bound to the same measure, set on the **map visual's own** title field, stayed blank on every click. Likely explanation: a click on a point within a visual behaves as a highlight within that visual's own rendering, not necessarily as a full single-row filter of that visual's own overall context, so a title evaluated against the visual's own context still saw all 158 stations. Confirmed as a genuine platform quirk (blank, not stale-and-wrong) rather than a data type or measure issue, since the same measure worked immediately elsewhere.

**Fix**: moved the title out of the map's own title field entirely, into a separate **card visual** positioned above the map and styled to read as a heading (Category label switched off in the card's Format pane, since it otherwise displays the measure's name — "Map Title" — above the value).

## What We Built

- `update_dim_parameters.py` — one-off script adding `corr_m_id`/`corr_d_id` to `dim_parameters`, mapping daily ↔ monthly parameter pairs by shortname transformation
- Three measures on `lf-ogd-smn_m`/`lf-ogd-smn_d`: `Historical Average`, `This Year Average`, `This Year Daily Point`
- One text-typed measure for the dynamic chart title
- Report page with two line charts (year-level and month-level historical comparisons) and a station map, all with per-visual interaction scoping and title workarounds as needed
- `powerBI/` folder added to the project (`.pbix` file, plus a PDF export as a point-in-time example of the report — not kept in sync with the live file)

## Next Steps

- Lesson 10: Terraform — codifying the now-stable architecture as infrastructure as code