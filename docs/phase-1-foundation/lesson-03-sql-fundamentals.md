# Lesson 3: SQL Fundamentals

## Overview

This lesson covered SQL basics through hands-on implementation: setting up Azure SQL Database, designing a relational schema, and loading real data via Python.

## Concepts Learned

### SQL Basics
- **SQL (Structured Query Language)**: Standard language for querying and managing relational databases
- **Relational databases**: Organize data into tables with rows and columns
- **ACID properties**: Atomicity, Consistency, Isolation, Durability (data integrity guarantees)

### Azure SQL Database
- **Single database model**: Ideal for focused workloads (vs Managed Instance for complex scenarios)
- **DTU-based pricing**: Simplified abstraction bundling CPU, memory, storage
- **Service tiers**: Basic, Standard, Premium (chose Basic for learning)
- **Firewall rules**: Control which IP addresses can connect
- **Authentication**: SQL Server auth (simple) vs Azure AD (enterprise)

### Schema Design
- **Primary key**: Uniquely identifies each row (composite key for multi-column uniqueness)
- **NOT NULL constraint**: Ensures columns always have data
- **Data types**: TEXT, VARCHAR(n), INT, FLOAT, DATETIME
- **Normalization**: Organizing data to reduce redundancy

### Data Types in SQL Server
| Type | Use Case | Example |
|------|----------|---------|
| CHAR(n) | Fixed-length text | Station abbreviations |
| VARCHAR(n) | Variable-length text | Descriptions |
| INT | Whole numbers | Counts |
| FLOAT | Decimal numbers | Measurements |
| DATETIME | Timestamps | Measurement times |

### pyodbc & Python Integration
- **pyodbc**: Python library connecting to SQL databases via ODBC drivers
- **ODBC drivers**: Platform-specific software enabling database connections
- **Parameterized queries**: Using `?` placeholders prevents SQL injection
- **Connection strings**: Format: `Driver={...};Server=...;Database=...;Uid=...;Pwd=...;`
- **Data type conversion**: numpy types must convert to Python native types for SQL insertion

## What We Built

**Azure SQL Server:** `sqls-nkipermeteo-dev`  
**Database:** `db-nkipermeteo`  
**Table:** `[ogd-smn_beh_d_recent]`

**Schema:**
- Composite primary key: (station_abbr, reference_timestamp)
- 41 columns total (station ID + 40 measurement parameters)
- Measurement values: FLOAT or INT
- Nullable columns for missing data

## Tools & Setup

**Installed:**
- VS Code + MSSQL extension (SQL query execution)
- pyodbc (Python-to-SQL connection)
- Microsoft ODBC Driver 17 for SQL Server (macOS: via DMG installer)

**Configuration:**
- Environment variables (`.env` file) for secure credential storage
- Connection string with ODBC driver specification
- Firewall rules allowing local machine IP + Azure services

## Scripts Created

**1. `generate_schema.py`**
- Reads CSV file
- Infers data types from pandas DataFrame
- Generates CREATE TABLE SQL statement
- Handles nullable columns and special characters

**2. `load_data.py`**
- Connects to Azure SQL via pyodbc
- Converts pandas data to Python native types
- Inserts rows using parameterized queries
- Commits transaction on success

## Key Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Table name with hyphens | Wrap in brackets: `[ogd-smn_beh_d_recent]` |
| Special characters in password | Use ODBC-compatible syntax in connection string |
| ODBC driver not found (macOS) | Install via Microsoft DMG installer |
| numpy data types in SQL | Convert using `.item()` method |
| Credentials in code | Store in `.env`, load via `python-dotenv` |

## Next Steps

- Write SELECT queries to explore the data
- Learn WHERE, ORDER BY, GROUP BY, JOINs
- Understand aggregation functions (COUNT, SUM, AVG)
- Practice window functions and CTEs