# Moodle Docker Setup

## Start

```bash
docker compose up -d
```

Wait ~3 minutes for Moodle to initialize on first run.

| Service | URL / Connection |
|---------|------------------|
| Moodle UI | http://localhost:8080 |
| Admin login | `admin` / `Admin123!` |
| MariaDB | `localhost:3306`, db `moodle`, user `moodle`, pass `moodle` |

> **Note:** Bitnami Moodle/MariaDB images were removed from Docker Hub in 2025.
> This project uses `erseco/alpine-moodle` + official `mariadb:11` instead.

## First-Time Moodle Configuration

1. Log in as admin
2. **Site Admin → Courses → Add a new course** — create the 9 courses from `docs/COURSE_CATALOG.md`
3. **Site Admin → Advanced Features** → Enable completion tracking
4. **Site Admin → Plugins → Enrolments** → Enable Manual enrolment
5. **Site Admin → Users → Upload users** — bulk upload from `data/processed/mdl_user.csv`
6. Set completion deadlines on mandatory courses to generate overdue scenarios

## Troubleshooting

### `bitnami/mariadb:11.4: not found`
Bitnami images were removed from Docker Hub. This project uses `mariadb:11` + `erseco/alpine-moodle` instead. Run:
```bash
git pull
docker compose pull
docker compose up -d
```

### Moodle restarts with `unicode` / UTF-8 error
The MariaDB volume was likely created without `utf8mb4`. Reset and start fresh:
```bash
docker compose down -v
rm -rf docker/mysqldata docker/moodledata
docker compose up -d
```
Wait 2–3 minutes, then open http://localhost:8080

## Stop

```bash
docker compose down
```

Data persists in `docker/moodledata/` and `docker/mysqldata/`. Moodle application files use a Docker named volume (`moodlehtml`).

First startup takes 2–3 minutes while Moodle installs.
