# Docker & SQL Setup and Analysis

---

## Docker Setup

### Checking Python image and pip version

Ran a Python 3.13 container to check the pip version:

```bash
docker run -it --rm --entrypoint=bash python:3.13
```

Inside the container:

```bash
pip --version
```

Found pip version: `25.3`

### Docker Compose Networking

Set up docker-compose with Postgres and pgAdmin. When configuring pgAdmin to connect to Postgres, I needed to understand how containers communicate within docker-compose. Within docker-compose, containers use the service name as hostname (not the container_name), so the service name is `db` (not `postgres`). Containers communicate on internal ports, not mapped host ports, so the internal Postgres port is `5432` (the `5433` is only for host access). Therefore, pgAdmin should connect using `db:5432`.

Here's the docker-compose.yaml configuration:

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

---

## Data Preparation

Downloaded the required datasets:

```bash
# Download green taxi data
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet

# Download zones lookup
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

### Load data into Postgres

Created a script to load the data:

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')

# Load green taxi data (parquet)
df = pd.read_parquet('green_tripdata_2025-11.parquet')
df.to_sql('green_taxi_trips', engine, if_exists='replace', index=False)
print(f'Loaded {len(df)} green taxi trips')

# Load zones
zones = pd.read_csv('taxi_zone_lookup.csv')
zones.to_sql('zones', engine, if_exists='replace', index=False)
print(f'Loaded {len(zones)} zones')
```

Ran the ingestion script:

```bash
uv run python ingest_green_data.py
```

---

## SQL Analysis Queries

### Count short trips in November 2025

Counted trips with distance <= 1 mile during November 2025:

```sql
SELECT COUNT(*)
FROM green_taxi_trips
WHERE lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1;
```

### Find day with longest trip distance

Identified which pickup day had the longest trip distance, excluding outliers (trips < 100 miles):

```sql
SELECT 
    CAST(lpep_pickup_datetime AS DATE) AS pickup_day,
    MAX(trip_distance) AS max_distance
FROM green_taxi_trips
WHERE trip_distance < 100
GROUP BY 1
ORDER BY max_distance DESC
LIMIT 1;
```

### Biggest pickup zone by total amount

Found the pickup zone with the largest total amount on November 18th, 2025:

```sql
SELECT 
    z."Zone",
    SUM(t.total_amount) AS total
FROM green_taxi_trips t
JOIN zones z ON t."PULocationID" = z."LocationID"
WHERE CAST(t.lpep_pickup_datetime AS DATE) = '2025-11-18'
GROUP BY z."Zone"
ORDER BY total DESC
LIMIT 1;
```

### Largest tip from East Harlem North

For passengers picked up in "East Harlem North" during November 2025, found which drop off zone had the largest tip:

```sql
SELECT 
    zdo."Zone" AS dropoff_zone,
    MAX(t.tip_amount) AS max_tip
FROM green_taxi_trips t
JOIN zones zpu ON t."PULocationID" = zpu."LocationID"
JOIN zones zdo ON t."DOLocationID" = zdo."LocationID"
WHERE zpu."Zone" = 'East Harlem North'
  AND t.lpep_pickup_datetime >= '2025-11-01'
  AND t.lpep_pickup_datetime < '2025-12-01'
GROUP BY zdo."Zone"
ORDER BY max_tip DESC
LIMIT 1;
```

---

## Terraform Workflow

Standard Terraform workflow for managing infrastructure:

| Step | Command | Purpose |
| ---- | ------- | ------- |
| Download plugins & setup backend | `terraform init` | Initializes working directory, downloads providers |
| Generate & auto-execute plan | `terraform apply -auto-approve` | `-auto-approve` skips the confirmation prompt |
| Remove all resources | `terraform destroy` | Removes all managed infrastructure |

The complete workflow sequence: `terraform init, terraform apply -auto-approve, terraform destroy`
