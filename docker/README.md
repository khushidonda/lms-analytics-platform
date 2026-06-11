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

> **Optional for class project.** The Power BI dashboard uses CSV files in `data/processed/`.
> Moodle is here if you want to explore how LMS databases store enrollment data.

## Load demo data

```bash
./seed/seed_moodle.sh
```

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
