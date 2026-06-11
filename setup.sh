#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "==> Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "==> Installing dependencies..."
pip install -q -r seed/requirements.txt

echo "==> Generating LMS dataset..."
python seed/generate_lms_data.py

echo "==> Exporting SQL analytics..."
python seed/run_sql_exports.py

echo ""
echo "Done! Next steps:"
echo "  1. Start Moodle: docker compose up -d"
echo "  2. Feed Moodle data: ./seed/seed_moodle.sh"
echo "  3. Build Power BI dashboard: see powerbi/POWERBI_SETUP.md"
