# Lesson 9 Cheatsheet: Dashboard & Report Design

## Cross-Granularity Parameter Correspondence

For two dimension rows representing the same real-world thing at different granularities, with a positional (not global) character difference in their natural key:

```python
sn = row['parameter_shortname']
m_mod_sn = sn[:-2] + 'm' + sn[-1]   # swap the one character before the trailing digit
d_mod_sn = sn[:-2] + 'd' + sn[-1]
```
Build a lookup once (`shortname -> parameter_id`), check membership against the lookup's keys (not `in` on a raw pandas Series — that checks the index, not the values), then `UPDATE ... SET corr_x_id = ? WHERE parameter_shortname = ?` with parameterized values (cast pandas types to native Python with e.g. `int(...)` before passing to pyodbc).

Do this as a **standalone script**, run after the initial load — it depends on `parameter_id` values that don't exist until after `IDENTITY` assigns them.

## DAX: `CALCULATE` Filter Interactions

- A `CALCULATE` filter on a column **replaces** a filter already on that same column from the visual's own axis/legend — this was directly verified in a table before trusting it in a chart.
- A filter that arrives at a table **through a relationship** (e.g., from a slicer on a related dimension) and an **explicit filter stated inside `CALCULATE` on the fact table's own column** do **not** simply override each other — they can combine into a contradiction that matches nothing.
```
  -- Wrong: relationship filter + explicit filter can conflict silently
  CALCULATE(AVERAGE(fact[value]), fact[parameter_id] = SomeOtherId)

  -- Fixed: clear the relationship-propagated filter first
  CALCULATE(AVERAGE(fact[value]), REMOVEFILTERS(fact), fact[parameter_id] = SomeOtherId)
```
- **Debug a blank measure by isolating it**: test each `SELECTEDVALUE`/lookup piece alone in a card first, then the full measure alone in a card, before trusting it inside a chart. A card confirms whether the *value* resolves; the chart/title only tells you *whether it displays*, which is a separate question.

## Line Chart: Only One Measure in Y-Axis

If a second measure replaces the first instead of adding a series: check the **Legend** field well. A populated Legend restricts the Y-axis to one measure. Remove the Legend field — multiple Y-axis measures auto-generate their own legend by series name.

## Dynamic Visual Title

1. Write a measure that returns a string.
2. Force its **data type to Text** explicitly (Fields pane / measure tools) — a measure left on the default numeric type is greyed out in the title's field picker even if it returns text.
3. Format pane → **General → Title** → `fx` next to the title field → bind the measure.
4. This works for the chart's overall **Title**; the **Y-axis title** field did not offer the same `fx` option in this version.

## Scoping a Slicer to Specific Visuals on a Shared Page

**Format ribbon → Edit interactions** (with the slicer selected) → per other visual on the page, choose **Filter** or **None**. Needed when two visuals on one page require the same slicer to behave differently (e.g., one needs a single selected value resolved via `SELECTEDVALUE`, the other needs the full unfiltered range on its own axis).

## Enabling Map Visuals

**File → Options and settings → Options → Security**, both **Current File** and **Global** sections. **Restart Power BI Desktop fully** — the setting did not take effect until relaunch.

## Click-to-Filter vs. a Visual's Own Title

Clicking a data point cross-filters **other** visuals correctly (verify with a test card and `SELECTEDVALUE`), but a title bound to the **same visual you clicked in** may not update — the click can act as a highlight within that visual rather than a full context change for its own title. Blank (not stale) output on the visual's own title, while the same measure works instantly elsewhere, points to this.

**Workaround**: use a separate **card visual** as a styled title above/beside the actual visual, instead of the visual's built-in title field.
- To hide the card's field-name label: Format pane → **Category label** → Off.

## Format vs. General Findings

| Symptom | Cause | Fix |
|---|---|---|
| 2nd measure replaces 1st on line chart | Legend field populated | Remove Legend field |
| Measure greyed out in title picker | Wrong/default data type | Set measure to Text |
| Title stays blank after clicking a point in the same visual | Click = highlight, not a full context change, for that visual's own title | Separate card as title, not the visual's own title field |
| Map visual disabled | Security setting off | Enable in both Current File and Global, then restart |