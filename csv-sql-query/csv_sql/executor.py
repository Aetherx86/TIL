import csv
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class ColumnTypeSpec:
    name: str
    sqlite_type: str

class SchemaInferrer:
    INT_RE = re.compile(r"^[+-]?[0-9]+$")
    REAL_RE = re.compile(r"^[+-]?[0-9]+\.[0-9]+$")

    @classmethod
    def infer_type(cls, samples: List[str]) -> str:
        non_empty = [s.strip() for s in samples if s and s.strip()]
        if not non_empty:
            return "TEXT"
        if all(cls.INT_RE.match(s) for s in non_empty):
            return "INTEGER"
        if all(cls.REAL_RE.match(s) or cls.INT_RE.match(s) for s in non_empty):
            return "REAL"
        return "TEXT"

class QueryOptimizer:
    """
    Extracts WHERE filter and JOIN columns from SQL queries to automatically
    generate optimal covering B-tree indexes prior to query execution.
    """
    WHERE_COL_RE = re.compile(r"(?:WHERE|AND|OR)\s+[\"'`]?([A-Za-z_][A-Za-z0-9_]*)[\"'`]?\s*(?:=|<|>|LIKE|IN)", re.IGNORECASE)
    JOIN_COL_RE = re.compile(r"(?:ON|USING)\s*\(\s*[\"'`]?([A-Za-z_][A-Za-z0-9_]*)[\"'`]?\s*=", re.IGNORECASE)

    @classmethod
    def suggest_indexes(cls, sql: str, table_name: str, valid_columns: List[str]) -> List[str]:
        cols = set(cls.WHERE_COL_RE.findall(sql) + cls.JOIN_COL_RE.findall(sql))
        cols = {c for c in cols if c in valid_columns}
        indexes = []
        for c in sorted(cols):
            indexes.append(f'CREATE INDEX IF NOT EXISTS "idx_{table_name}_{c}" ON "{table_name}" ("{c}")')
        return indexes

class CSVSQLExecutor:
    """
    High-performance CSV query engine with dynamic schema inference,
    automatic B-tree index compilation, and EXPLAIN QUERY PLAN inspection.
    """
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.table_columns: Dict[str, List[str]] = {}

    def load_csv(self, file_path: str, table_name: str, sample_rows: int = 100):
        path = Path(file_path)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            headers = next(reader)
            clean_headers = [h.strip().replace(" ", "_").replace("-", "_") for h in headers]
            self.table_columns[table_name] = clean_headers

            # Sample for type inference
            sample_data: List[List[str]] = []
            for _ in range(sample_rows):
                try:
                    row = next(reader)
                    sample_data.append(row)
                except StopIteration:
                    break

            inferred_types = []
            for col_idx in range(len(clean_headers)):
                col_samples = [r[col_idx] for r in sample_data if len(r) > col_idx]
                inferred_types.append(SchemaInferrer.infer_type(col_samples))

            col_defs = ", ".join([f'"{h}" {t}' for h, t in zip(clean_headers, inferred_types)])
            self.conn.execute(f'CREATE TABLE "{table_name}" ({col_defs})')

            # Insert sampled rows
            placeholders = ", ".join(["?"] * len(clean_headers))
            ins_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders})'
            if sample_data:
                self.conn.executemany(ins_sql, sample_data)

            # Insert remaining rows
            batch = []
            for row in reader:
                if len(row) == len(clean_headers):
                    batch.append(row)
                    if len(batch) >= 1000:
                        self.conn.executemany(ins_sql, batch)
                        batch.clear()
            if batch:
                self.conn.executemany(ins_sql, batch)
            self.conn.commit()

    def query(self, sql: str, auto_index: bool = True) -> Tuple[List[str], List[Tuple[Any, ...]]]:
        if auto_index:
            for tbl, cols in self.table_columns.items():
                if tbl.lower() in sql.lower():
                    for idx_stmt in QueryOptimizer.suggest_indexes(sql, tbl, cols):
                        self.conn.execute(idx_stmt)
            self.conn.commit()

        cur = self.conn.cursor()
        cur.execute(sql)
        headers = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()
        return headers, rows

    def explain(self, sql: str) -> List[Tuple[int, int, int, str]]:
        cur = self.conn.cursor()
        cur.execute(f"EXPLAIN QUERY PLAN {sql}")
        return cur.fetchall()
