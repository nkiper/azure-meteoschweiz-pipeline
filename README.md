# azure-meteoschweiz-pipeline

A self-directed learning project: building an end-to-end Azure data pipeline using real weather data from [MeteoSchweiz](https://www.meteoswiss.admin.ch/)'s open data platform, covering ETL/ELT, data warehousing, and BI reporting. Lessons generated interactively by Claude (Sonnet 5).

## Architecture

MeteoSchweiz API

↓ (download_data.py)

Local CSVs

↓ (upload_to_adls.py)

Azure Data Lake Storage Gen2 (raw/)

↓ (Databricks notebook: reshape, join dimensions)

├─→ ADLS Gen2 (processed/)

└─→ Azure SQL Database (star schema)

↓

Power BI


Daily weather data (158 SwissMetNet stations) feeds a long-format fact table (`lf-ogd-smn_d`); monthly historical data (1975–) feeds a second fact table (`lf-ogd-smn_m`) for year-over-year comparisons. Both share conformed `dim_stations` and `dim_parameters` dimensions. Full schema diagram and design notes in [`ARCHITECTURE.md`](ARCHITECTURE.md).

Core Azure resources (resource group, storage account, SQL server/database, Databricks workspace) are managed with Terraform — see `terraform/`.

## Repo Structure

- `docs/` — lesson-by-lesson summaries and cheatsheets (`docs/phase-N-*/`), plus `ARCHITECTURE.md` and `PROGRESS.md` (full roadmap and status)
- `scripts/setup/` — Python scripts: data download/upload, dimension table schema generation and loading
- `scripts/sql/` — saved SQL scripts
- `scripts/databricks/` — the notebook(s) used for transformation and loading
- `powerBI/` — the Power BI report (`.pbix`) and an example PDF export
- `terraform/` — infrastructure as code for core Azure resources
- `data/` — local raw/processed data (git-ignored)

## Running It

```bash
scripts/setup/update_data_adls.zsh            # downloads new data and uploads it to ADLS (runs download_data.py + upload_to_adls.py)
```

Run `python scripts/setup/download_data.py` on its own only if you want the raw CSVs locally without uploading.

Azure credentials and connection strings are supplied via a local `.env` file (not committed). See `docs/` for setup details per lesson.

## Status

All five phases (Foundation, ETL, Data Warehouse, Analytics & BI, Infrastructure as Code) are complete. See [`PROGRESS.md`](PROGRESS.md) for the full lesson-by-lesson history and known open items.