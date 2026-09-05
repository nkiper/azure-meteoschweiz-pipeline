# Lesson 3 Cheatsheet: SQL Fundamentals & Azure SQL Setup

## Quick Reference

### Azure SQL Setup Checklist
- [ ] Create SQL Server in Resource Group
- [ ] Configure firewall rules (allow client IP + Azure services)
- [ ] Choose authentication method (SQL Server auth for learning)
- [ ] Create admin login and password
- [ ] Get connection string from Azure Portal

### Table Design Pattern
```sql
CREATE TABLE [table_name] (
    column1 DATATYPE NOT NULL,
    column2 DATATYPE,
    column3 DATATYPE,
    PRIMARY KEY (column1, column2)
);
```

### Data Types Quick Reference

CHAR(3) -- Fixed 3 characters (station_abbr)
VARCHAR(255) -- Variable text, up to 255 chars (fallback)
INT -- Whole numbers
FLOAT -- Decimal numbers
DATETIME -- Date and time


### Connection String Format (ODBC)

Driver={ODBC Driver 17 for SQL Server};
Server=<server-name>.database.windows.net;
Database=<database-name>;
Uid=<username>;
Pwd=<password>;


### Python pyodbc Workflow
```python
import pyodbc

# Connect
connection = pyodbc.connect(CONNECTION_STRING)
cursor = connection.cursor()

# Execute with parameters
cursor.execute("INSERT INTO table VALUES (?, ?, ?)", (val1, val2, val3))

# Commit & close
connection.commit()
cursor.close()
connection.close()
```

### Secure Credentials Management
**`.env` file (add to `.gitignore`):**

AZURE_SQL_CONNECTION_STRING=Driver={...};Server=...;Uid=...;Pwd=...;


**Python code:**
```python
from dotenv import load_dotenv
import os

load_dotenv()
connection_string = os.getenv('AZURE_SQL_CONNECTION_STRING')
```

### Common SQL Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Invalid object name` | Table doesn't exist | Create table first with CREATE TABLE |
| `Login failed for user` | Wrong password or username | Verify credentials in Query Editor first |
| `Invalid parameter type` | numpy types in Python | Convert with `.item()` or native Python types |
| `Data source name not found` | ODBC driver missing | Install Microsoft ODBC Driver for your OS |

### Composite Primary Key
Ensures combination of columns is unique:
```sql
PRIMARY KEY (station_abbr, reference_timestamp)
```
One measurement per station per day = guaranteed uniqueness.

### Nullable Columns in SQL
```sql
column_name INT              -- NOT NULL by default (required)
column_name INT NULL         -- Explicitly nullable
column_name INT NOT NULL     -- Explicitly required
```

In Python: Use `None` for SQL NULL values.

### Parameterized Queries (Safe)
```python
# SAFE: Prevents SQL injection
cursor.execute("INSERT INTO table VALUES (?, ?)", (user_input, value))

# UNSAFE: Don't do this!
cursor.execute(f"INSERT INTO table VALUES ('{user_input}', {value})")
```

### Testing Connection
```sql
-- In Query Editor or VS Code
SELECT 1 AS test          -- If this works, you're connected
SELECT COUNT(*) FROM table_name  -- Verify table exists and has data
```

### File Structure

scripts/
├── setup/
│ ├── generate_schema.py (CSV → CREATE TABLE)
│ └── load_data.py (CSV → SQL INSERT)
└── sql/
└── create-tbl-*.sql (Generated SQL scripts)

data/
├── raw/
│ └── ogd-smn_beh_d_recent.csv
├── processed/
└── docs/

requirements.txt (pandas, pyodbc)
.env (credentials - in .gitignore!)


### Environment Setup
```bash
# Create venv
python -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run script
python scripts/setup/load_data.py
```