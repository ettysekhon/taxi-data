# Workflow Orchestration with Kestra

Open-source orchestration platform for data pipelines.

---

## Contents

- [Setup](#setup)
- [Core Concepts](#core-concepts)
- [Python Tasks](#python-tasks)
- [ETL Pipeline](#etl-pipeline)
- [Loading Taxi Data](#loading-taxi-data)
- [Scheduling & Backfills](#scheduling--backfills)
- [Homework Tasks](#homework-tasks)
- [GCP Setup](#gcp-setup)
- [Troubleshooting](#troubleshooting)

---

## Setup

```bash
cd taxi-data/workflow-orchestration
docker compose up -d
```

Access Kestra: <http://localhost:8080>  
Login: `admin@kestra.io` / `Admin1234`

### Storage Configuration

Changed from Docker volume to local directory for easier file access:

```yaml
# docker-compose.yml
volumes:
  - ./kestra-storage:/app/storage  # Local directory mount
```

Files accessible at: `./kestra-storage/main/zoomcamp/<flow-id>/executions/<execution-id>/tasks/`

---

## Core Concepts

| Concept | Purpose |
| ------- | ------- |
| Flow | Container for tasks |
| Tasks | Steps within a flow |
| Inputs | Runtime parameters |
| Outputs | Data passed between tasks |
| Triggers | Auto-start flows (schedule/event) |
| Variables | Reusable values |

Created `01_hello_world` flow to test concepts. Variables render using `{{inputs.name}}` syntax.

---

## Python Tasks

Created `02_python` flow. Key points:

- `taskRunner: docker` runs Python in isolated container
- `dependencies` installs pip packages
- `Kestra.outputs()` sends data back to Kestra

---

## ETL Pipeline

Created `03_getting_started_data_pipeline` flow demonstrating:

```text
Extract (HTTP) → Transform (Python) → Query (DuckDB)
```

### Inputs and Outputs

- **Inputs**: `{{inputs.columns_to_keep}}` — workflow-level parameters
- **Outputs**: `{{outputs.extract.uri}}` — task outputs referenced by subsequent tasks
- **Output files**: `{{outputs.transform.outputFiles['products.json']}}` — file references

Output files only visible on producing task, not consuming tasks.

---

## Loading Taxi Data

Created `04_postgres_taxi` flow. Pattern:

```text
Select inputs → Extract CSV → Create tables → Load staging → Merge to final
```

### Variables

```yaml
variables:
  file: "{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv"
  table: "public.{{inputs.taxi}}_tripdata"
```

### Conditional Logic

```yaml
- id: if_yellow_taxi
  type: io.kestra.plugin.core.flow.If
  condition: "{{inputs.taxi == 'yellow'}}"
```

### Plugin Defaults

```yaml
pluginDefaults:
  - type: io.kestra.plugin.jdbc.postgresql
    values:
      url: jdbc:postgresql://pgdatabase:5432/ny_taxi
      username: root
      password: root
```

### Disabling Tasks

To preserve output files for inspection:

```yaml
- id: purge_files
  type: io.kestra.plugin.core.storage.PurgeCurrentExecutionFiles
  disabled: true
```

---

## Scheduling & Backfills

Created `05_postgres_taxi_scheduled` flow with triggers:

```yaml
triggers:
  - id: yellow_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 10 1 * *"
    timezone: America/New_York
    inputs:
      taxi: yellow
```

### Running a Backfill

1. Open flow → **Triggers** tab
2. Click **⋯** next to trigger → **Backfill executions**
3. Set date range (e.g., `2020-01-01` to `2020-12-31`)
4. Execute

Creates one execution per month in the range.

---

## Homework Tasks

### Task 1: File Size Check

Ran `04_postgres_taxi` with inputs:

- taxi: `yellow`
- year: `2020`
- month: `12`

Disabled `purge_files` task, then checked file size in **Outputs** tab → `extract` task → `outputFiles`.

Alternatively, accessed file directly:

```bash
ls -lh ./kestra-storage/main/zoomcamp/04-postgres-taxi/executions/<id>/tasks/extract/<id>/*.csv
```

### Task 2: Variable Rendering

Checked rendered variable value in execution with:

- taxi: `green`
- year: `2020`
- month: `04`

Variable definition:

```yaml
file: "{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv"
```

### Task 3: Yellow Taxi 2020 Row Count

Ran backfill on `05_postgres_taxi_scheduled` for yellow taxi:

- Start: `2020-01-01`
- End: `2020-12-31`

Then queried:

```sql
SELECT COUNT(*) 
FROM public.yellow_tripdata 
WHERE filename LIKE 'yellow_tripdata_2020-%';
```

### Task 4: Green Taxi 2020 Row Count

Ran backfill for green taxi, same date range.

```sql
SELECT COUNT(*) 
FROM public.green_tripdata 
WHERE filename LIKE 'green_tripdata_2020-%';
```

### Task 5: Yellow Taxi March 2021 Row Count

Ran `04_postgres_taxi` with:

- taxi: `yellow`
- year: `2021` (added to flow inputs first)
- month: `03`

```sql
SELECT COUNT(*) 
FROM public.yellow_tripdata 
WHERE filename = 'yellow_tripdata_2021-03.csv';
```

### Task 6: Timezone Configuration

Added timezone to Schedule trigger:

```yaml
triggers:
  - id: yellow_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 10 1 * *"
    timezone: America/New_York
    inputs:
      taxi: yellow
```

---

## Database Access

### pgAdmin

URL: <http://localhost:8085>  
Login: `admin@admin.com` / `root`

Connection:

- Host: `pgdatabase`
- Port: `5432`
- Database: `ny_taxi`
- User: `root`
- Password: `root`

### Direct Access

```bash
docker exec -it workflow-orchestration-pgdatabase-1 psql -U root -d ny_taxi
```

### Database Architecture

| Database | Purpose | Access |
| -------- | ------- | ------ |
| `ny_taxi` | Taxi trip data | pgAdmin / psql |
| `kestra` | Kestra metadata | Internal only |

---

## GCP Setup

### ETL vs ELT

Local Postgres uses **ETL**: Extract → Transform locally → Load to database.

GCP uses **ELT**: Extract → Load to GCS (data lake) → Transform in BigQuery (data warehouse).

ELT leverages cloud compute for transforming large datasets — faster than local processing.

### Prerequisites

- GCP Project ID
- Service Account with BigQuery Admin + Storage Admin roles
- Service Account JSON key

### Add GCP Credentials to Kestra

> **Security:** `GCP_CREDS` contains sensitive data. Never commit to Git. Use KV Store or Secrets.

1. **Namespaces** → `zoomcamp` → **KV Store**
2. Add key: `GCP_CREDS`
3. Value: Paste service account JSON

### Set GCP Configuration

Create and execute `06_gcp_kv.yaml`:

```yaml
id: 06_gcp_kv
namespace: zoomcamp

tasks:
  - id: gcp_project_id
    type: io.kestra.plugin.core.kv.Set
    key: GCP_PROJECT_ID
    kvType: STRING
    value: YOUR-PROJECT-ID

  - id: gcp_location
    type: io.kestra.plugin.core.kv.Set
    key: GCP_LOCATION
    kvType: STRING
    value: us-central1

  - id: gcp_bucket_name
    type: io.kestra.plugin.core.kv.Set
    key: GCP_BUCKET_NAME
    kvType: STRING
    value: your-unique-bucket-name

  - id: gcp_dataset
    type: io.kestra.plugin.core.kv.Set
    key: GCP_DATASET
    kvType: STRING
    value: zoomcamp
```

### Create GCS Bucket and BigQuery Dataset

Create and execute `07_gcp_setup.yaml`:

```yaml
id: 07_gcp_setup
namespace: zoomcamp

tasks:
  - id: create_gcs_bucket
    type: io.kestra.plugin.gcp.gcs.CreateBucket
    ifExists: SKIP
    storageClass: REGIONAL
    name: "{{kv('GCP_BUCKET_NAME')}}"

  - id: create_bq_dataset
    type: io.kestra.plugin.gcp.bigquery.CreateDataset
    name: "{{kv('GCP_DATASET')}}"
    ifExists: SKIP

pluginDefaults:
  - type: io.kestra.plugin.gcp
    values:
      serviceAccount: "{{kv('GCP_CREDS')}}"
      projectId: "{{kv('GCP_PROJECT_ID')}}"
      location: "{{kv('GCP_LOCATION')}}"
      bucket: "{{kv('GCP_BUCKET_NAME')}}"
```

### Verify KV Store

Before proceeding, confirm all keys exist in **Namespaces** → `zoomcamp` → **KV Store**:

- `GCP_CREDS`
- `GCP_PROJECT_ID`
- `GCP_LOCATION`
- `GCP_BUCKET_NAME`
- `GCP_DATASET`

### Load Taxi Data to BigQuery

Use `08_gcp_taxi.yaml` for manual loads, `09_gcp_taxi_scheduled.yaml` for scheduled loads with backfill capability.

Data flow:

```text
Extract CSV → Upload to GCS → Create External Table → Create Monthly Table → Merge to Main Table
```

### GCP Verification

After executing flows, verify in GCP Console:

- GCS Bucket: <https://console.cloud.google.com/storage/browser>
- BigQuery: <https://console.cloud.google.com/bigquery>

Tables created: `<taxi>_tripdata` (main), `<taxi>_tripdata_YYYY_MM` (monthly), `<taxi>_tripdata_YYYY_MM_ext` (external)

---

## Quick Reference

| Service | URL |
| ------- | --- |
| Kestra | <http://localhost:8080> |
| pgAdmin | <http://localhost:8085> |

| Command | Purpose |
| ------- | ------- |
| `docker compose up -d` | Start services |
| `docker compose down` | Stop services |
| `docker compose down -v` | Stop and remove volumes |
| `docker compose logs -f kestra` | View logs |

---

## Troubleshooting

### Image Versions

Pin versions for reproducibility:

- Kestra: `kestra/kestra:v1.1`
- Postgres: `postgres:18`

### Port Conflicts

If port 8080 is in use, modify `docker-compose.yml`:

```yaml
ports:
  - "18080:8080"
```

Access Kestra at <http://localhost:18080> instead.

### BigQuery CSV Column Mismatch

Error like:

```text
CSV table references column position 17, but line contains only 14 columns
```

**Cause:** Incomplete CSV download or upload due to network issues.

**Fix:** Re-run entire execution including re-downloading the CSV file.

### Import Flows via API

Alternative to UI for adding flows:

```bash
curl -X POST -u 'admin@kestra.io:Admin1234' \
  http://localhost:8080/api/v1/flows/import \
  -F fileUpload=@flows/04_postgres_taxi.yaml
```

---

## Cleanup

```bash
docker compose down -v
```

GCP resources (if created):

```bash
gsutil rm -r gs://YOUR-BUCKET-NAME
bq rm -r -f YOUR_PROJECT:zoomcamp
```
