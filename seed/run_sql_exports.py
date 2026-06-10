#!/usr/bin/env python3
"""Run all SQL analytics queries and export results to data/processed/."""

from pathlib import Path
import sqlite3

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "lms.db"
SQL_DIR = ROOT / "sql"
OUT_DIR = ROOT / "data" / "processed"

QUERIES = [
    "01_enrollment_summary.sql",
    "02_overdue_compliance.sql",
    "03_participation_trend.sql",
    "04_data_validation.sql",
    "05_compliance_score.sql",
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    for filename in QUERIES:
        sql = (SQL_DIR / filename).read_text()
        df = pd.read_sql_query(sql, conn)
        out_name = filename.replace(".sql", ".csv")
        out_path = OUT_DIR / out_name
        df.to_csv(out_path, index=False)
        print(f"Wrote {out_path} ({len(df)} rows)")

    conn.close()


if __name__ == "__main__":
    main()
