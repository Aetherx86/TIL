# csv-sql-query

Execute ANSI SQL queries directly against CSV and TSV files via in-memory SQLite.

## Overview

Analyzing structured CSV and TSV export files often involves ad-hoc pandas scripts or manual spreadsheet manipulation. `csv-sql-query` automatically loads CSV files into an in-memory SQLite relational database, enabling instant SQL joins, aggregations, and subqueries directly from the terminal.

## Features

- In-Memory Performance: Fast querying powered by SQLite's memory database engine.
- Multi-Table Joins: Load multiple CSV files simultaneously into distinct tables to execute relational joins.
- Automatic Header Sanitization: Replaces invalid SQL characters in column headers with clean underscore identifiers.
- Zero Dependencies: Uses Python's built-in `sqlite3` and `csv` modules.

## Installation

```bash
git clone https://gitlab.com/jk9576/csv-sql-query.git
cd csv-sql-query
pip install -e .
```

## CLI Usage

### Query Single Table

```bash
csv-sql --table employees.csv=emp "SELECT department, COUNT(*) as count FROM emp GROUP BY department"
```

### Relational Join Across Files

```bash
csv-sql --table orders.csv=orders --table users.csv=users   "SELECT users.name, orders.total FROM orders JOIN users ON orders.user_id = users.id WHERE orders.total > 100"
```

## Python API Usage

```python
from csv_sql.executor import CSVSQLExecutor

executor = CSVSQLExecutor()
executor.load_csv("sales.csv", "sales")
headers, rows = executor.query("SELECT region, SUM(amount) FROM sales GROUP BY region")
for row in rows:
    print(row)
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
