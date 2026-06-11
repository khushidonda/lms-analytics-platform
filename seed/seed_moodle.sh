#!/usr/bin/env bash
# Load CSV data into the live Moodle database (Docker must be running).
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Checking Docker services..."
docker compose ps --status running | grep -q moodle || {
  echo "Start Moodle first: docker compose up -d"
  exit 1
}

echo "==> Regenerating analytics CSVs (if needed)..."
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi
python seed/generate_lms_data.py
python seed/run_sql_exports.py

echo "==> Seeding Moodle (users, courses, enrollments)..."
docker exec lms-analytics-platform-moodle-1 php /seed-scripts/moodle_seed.php

echo ""
echo ""
echo "Tip: For a clean Moodle reset, run:"
echo "  docker compose down -v && rm -rf docker/mysqldata docker/moodledata && docker compose up -d"
echo "  then re-run this script."
echo ""
echo "Done! Open http://localhost:8080"
echo "  Admin:   admin / Admin123!"
echo "  Student: any username in data/processed/mdl_user.csv / Student123!"
