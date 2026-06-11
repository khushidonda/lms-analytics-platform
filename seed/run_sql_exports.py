#!/usr/bin/env python3
"""Run SQL analytics queries and export results to data/processed/."""

from pathlib import Path
import sqlite3

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "lms.db"
SQL_DIR = ROOT / "sql"
OUT_DIR = ROOT / "data" / "processed"

QUERIES = [
    "01_enrollment_summary.sql",
    "02_incomplete_courses.sql",
    "03_participation_trend.sql",
    "04_data_validation.sql",
    "05_program_completion_summary.sql",
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    for filename in QUERIES:
        sql = (SQL_DIR / filename).read_text()
        df = pd.read_sql_query(sql, conn)
        out_path = OUT_DIR / filename.replace(".sql", ".csv")
        df.to_csv(out_path, index=False)
        print(f"Wrote {out_path} ({len(df)} rows)")

    conn.close()


if __name__ == "__main__":
    main()
