# Kestra Workflow Orchestration on GCP — Complete Walkthrough Guide

This guide walks you through setting up Kestra (an open-source workflow orchestrator) on your local machine via Docker, connecting it to GCP, and progressively building more advanced data pipelines using BigQuery, GCS, GitHub sync, subflows, parallel processing, error handling, event-driven triggers, AI agents, and dashboards.

## What We're Building

A complete workflow orchestration platform that:

* Runs Kestra locally via Docker Compose (Postgres-backed)
* Connects to GCP (GCS buckets + BigQuery datasets)
* Runs Python and Java code inside containerised tasks
* Syncs flows/files from GitHub (GitOps)
* Ingests ecommerce data (CSV → GCS → BigQuery raw → BigQuery clean)
* Ingests NYC Yellow Cab taxi data (Parquet → GCS → BigQuery) — sequentially, then in parallel with subflows
* Implements error handling with retry logic and rollback
* Triggers pipelines from GCS file-upload events via Pub/Sub
* Adds an AI assistant (Gemini) to Kestra for debugging
* Creates a YAML-based monitoring dashboard

## Prerequisites

* A Google account with billing enabled
* Docker Desktop installed and running
* Git installed
* A GitHub account (free is fine)
* Python 3 installed locally (for the base64 helper script)
* ~10 GB free disk space (Docker images + data files)

## Estimated Total Time: 4–6 hours

Breakdown per section below. Times assume you're following along and not debugging heavily. GCP console lag and Docker image pulls are the biggest variables.

---

## Phase 1 — GCP Account & Kestra Setup (doc 1_3)

Estimated time: 45–60 min

### Step 1.1 — Create GCP project

1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Sign in, create a new project (e.g. `kestra-demo`)
3. Attach a billing account (required for APIs)

**Cost warning:** BigQuery and GCS operations can incur costs. Stay within free-tier limits where possible and double-check before running large queries.

### Step 1.2 — Install the GCP CLI

On Mac:

```bash
curl https://sdk.cloud.google.com | bash
```

See all your configurations:

```bash
gcloud config configurations list
```

Create a new configuration for the new account (so you can switch between projects cleanly):

```bash
gcloud config configurations create kestra-demo
```

This will prompt you to log in with the new account:

```bash
gcloud init
```

During `gcloud init`, select your project (e.g. `kestra-demo`).

Switch between configurations anytime:

```bash
gcloud config configurations activate default   # your old one
gcloud config configurations activate kestra-demo  # the new one
```

### Step 1.3 — Enable required APIs

```bash
gcloud services enable storage.googleapis.com
gcloud services enable bigquery.googleapis.com
```

### Step 1.4 — Create a GCS bucket

Pick a globally unique name (e.g. `com-yourname-kestra-demo`):

```bash
gsutil mb -l europe-west2 gs://com-yourname-kestra-demo/
gsutil ls  # verify
```

### Step 1.5 — Create a BigQuery test dataset

```bash
bq mk --dataset --location=europe-west2 kestra_test
bq ls  # verify
```

### Step 1.6 — Create a GCP service account + permissions

```bash
gcloud iam service-accounts create kestra-sa --display-name="Kestra Service Account"
PROJECT_ID=$(gcloud config get-value project)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:kestra-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/bigquery.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:kestra-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

(For production, use least-privilege roles instead of `admin`.)

### Step 1.7 — Generate the JSON key

```bash
gcloud iam service-accounts keys create ~/kestra-gcp-key.json \
  --iam-account=kestra-sa@${PROJECT_ID}.iam.gserviceaccount.com
ls -lh ~/kestra-gcp-key.json  # verify
```

### Step 1.8 — Base64-encode the key and create `.env_encoded`

Use the provided helper script (`helper_scripts/quick_base64_encode.py`) — **never** use an online converter.

One-liner to create `.env_encoded` in the project root:

```bash
echo "SECRET_GCP_SERVICE_ACCOUNT=$(base64 < ~/kestra-gcp-key.json)" > .env_encoded
head -c 80 .env_encoded  # verify
```

On Linux, use `base64 -w 0` to avoid line wraps when encoding manually.

### Step 1.9 — Start Kestra via Docker Compose

```bash
docker compose -f docker-compose.yml up
```

Kestra UI will be at [http://localhost:8080](http://localhost:8080) (login: `admin@kestra.io` / `Admin1234`).

The `docker-compose.yml` runs Kestra v1.1.7 with a Postgres backend.

### Step 1.10 — Create and run the GCS connection test flow

In Kestra UI → Flows → Create, paste the contents of `flows/dev.testing/flows/1_3/1_3-test-gcs-connection.yaml`.

**Important:** Replace `gs://com-mycompany-kestra-demo/` with your actual bucket name.

Execute the flow, then verify:

```bash
gsutil cat gs://com-yourname-kestra-demo/test/hello.txt
```

Expected output: `Hello from Kestra! GCP connection works! 🎉`

---

## Phase 2 — Running Code & GitOps (docs 2_1, 2_2, 2_3)

Estimated time: 60–90 min

### Step 2.1 — Run Python code in Kestra

Create these flows in the `dev.testing` namespace:

1. **Inline Python** — `flows/dev.testing/flows/2_1/python-data-processing.yaml` — installs pandas, creates sample data, outputs CSV
2. **Namespace files** — Upload `flows/dev.testing/files/process_sales_data.py` as a namespace file, then create `flows/dev.testing/flows/2_1/python-with-namespace-files.yaml`
3. **Multi-step data exchange** — `flows/dev.testing/flows/2_1/python-multistep.yaml` — generates CSV in step 1, reads it in step 2 via `inputFiles`/`outputFiles`

Execute each and verify logs/outputs.

### Step 2.2 — Run Java code in Kestra

Create these flows:

1. **Inline Java** — `flows/dev.testing/flows/2_1/java-hello-world.yaml` — compiles & runs in `eclipse-temurin:17-jdk` container (takes a few minutes)
2. **Namespace file Java** — Upload `DataProcessor.java`, create `java-with-namespace-files.yaml`
3. **Maven project** — Upload `pom.xml` + `src/main/java/com/example/MavenDataProcessor.java` as namespace files, create `java-maven-project.yaml`

### Step 2.3 — Sync code from GitHub (GitOps)

#### Prerequisites for this step

* Fork or clone the [kestra-demo repo](https://github.com/andkret/kestra-demo)
* Create a GitHub Personal Access Token (PAT)
* Base64-encode and add these secrets to `.env_encoded`:

```bash
SECRET_GITHUB_TOKEN=<base64-encoded PAT>
SECRET_KESTRA_USER=<base64-encoded "admin@kestra.io">
SECRET_KESTRA_PASSWORD=<base64-encoded "Admin1234">
```

Run the [quick_base64_encode script](helper_scripts/quick_base64_encode.py) for each of these secrets and add to `.env_encoded`.

* Restart Docker Compose after updating `.env_encoded`

#### NamespaceSync (single namespace)

Create `flows/dev.testing/flows/2_2/sync-project-code.yaml` — syncs the `data-processing` directory to the `dev.testing` namespace. Replace `YOUR-USERNAME` with your GitHub username.

#### TenantSync (multi-namespace)

Create `flows/dev.testing/flows/2_2/tenant-sync-flow.yaml` in the `system` namespace — reads the Git folder structure and distributes files to `dev.testing`, `common`, `data-processing` namespaces automatically.

**Note:** In Kestra OSS, namespaces are created implicitly when you run a flow targeting them. If the namespaces don't exist yet, create a trivial flow in each first.

### Step 2.4 — Subflows (reusable modular flows)

Create both flows in `dev.testing` namespace:

1. **Subflow** — `critical_service_subflow.yaml` — downloads orders CSV, runs a DuckDB aggregation, returns output
2. **Parent flow** — `parent_service.yaml` — calls the subflow with `wait: true` and `transmitFailed: true`, then logs the result

Key concepts: `wait`, `transmitFailed`, passing outputs between parent and subflows.

---

## Phase 3 — Real Data Pipelines (docs 3_1 through 3_5)

Estimated time: 90–120 min

### Step 3.1 — Ecommerce ingest & clean pipeline

#### Ecommerce GCP setup

Create two BigQuery datasets:

```bash
bq mk --dataset --location=europe-west2 YOUR_PROJECT:raw
bq ls  # verify
```

```bash
bq mk --dataset --location=europe-west2 YOUR_PROJECT:clean
bq ls  # verify
```

#### Upload data

Unzip `data-files/ecommerce.zip` and upload the CSV to your GCS bucket as `data.csv`.

#### Create and run the ecommerce flow

Use `flows/gcp.ecommerce/flows/3_1/ecommerce_ingest_and_clean_with_errors.yaml`.

**Replace** `projectId`, `input_bucket` variables with your values.

This flow:

1. Loads raw CSV from GCS → BigQuery `raw.transactions_raw`
2. Creates `clean.transactions` — casts types, filters bad rows (negative qty, cancellations)
3. Creates `clean.transactions_errors` — captures rejected rows

### Step 3.2 — Yellow Cab sequential ingest

#### Yellow Cab GCP setup

```bash
bq mk --dataset --location=europe-west2 YOUR_PROJECT:YellowCab
bq ls  # verify
```

Download multiple months of Parquet files from the [NYC TLC Trip Record page](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) and upload them to `gs://YOUR_BUCKET/yellow-cab/`.

#### Create and run the sequential ingest flow

Use `flows/gcp.yellowcab/flows/3_2/yellow_cab_sequential_ingest.yaml`. Replace `bucket` variable.

This flow:

1. Lists all files in `yellow-cab/`
2. Iterates with `ForEach`, loads each Parquet into `YellowCab.raw_data`

Optionally add `concurrencyLimit: 5` to the ForEach task for parallel loading.

### Step 3.3 — Yellow Cab parallel pipeline with subflow

#### Upload lookup file

Upload `data-files/taxi_zone_lookup.csv` to your GCS bucket root.

#### Create both Yellow Cab main flows

1. **Main flow** — `yellow_cab_main.yaml` — lists files, parallel-loads to BigQuery, calls subflow, then archives & deletes source files
2. **Subflow** — `yellow_cab_subflow.yaml` — loads taxi zone lookup, enriches trips via JOIN, runs parallel special-trip detection (suspicious, short, long, invalid GPS), parallel aggregations (per borough, per hour), creates final curated table

**Replace** all `bucket` and project ID references with your values.

This is the most complex pipeline — it demonstrates:

* `ForEach` with `concurrencyLimit` for parallel GCS→BQ loading
* Subflow orchestration
* `Parallel` task groups for independent BQ queries
* File archiving and cleanup

### Step 3.4 — Error handling with retry & rollback

#### Retry GCP setup

1. Create folder `yc-retry/data/` in your GCS bucket
2. Upload `data-files/retry-ok-file.csv` and `data-files/retry-error-file.csv` into that folder
3. Create BigQuery dataset `yc_retry` (same location as your bucket, e.g. europe-west2)

#### Create retry flows

1. **Main flow** — `yellow_cab_retry_main.yaml` — iterates files, loads each into an isolated staging table, calls a cleaning subflow, then archives/deletes on success or rolls back + moves to error folder on failure
2. **Subflow** — `yellow_cab_retry_subflow.yaml` — tries strict INSERT first; if it fails, falls back to a SAFE_CAST "soft" insert; only fails the flow if both paths fail

Key concepts: `allowFailure`, `errors` handlers, `retry` with exponential backoff, per-file isolation via dynamic staging tables, rollback via DELETE, file routing (archive vs error folder).

### Step 3.5 — Event-driven pipeline (GCS → Pub/Sub → Kestra)

#### Pub/Sub setup

Set your variables:

```bash
PROJECT="your-project-id"
TOPIC="file-upload-events"
SUB="file-upload-sub"
BUCKET="your-bucket-name"
```

Run these commands to create the infrastructure:

```bash
# Enable Pub/Sub API
gcloud services enable pubsub.googleapis.com

# Create topic and subscription
gcloud pubsub topics create "$TOPIC" --project "$PROJECT"
gcloud pubsub subscriptions create "$SUB" --project "$PROJECT" --topic "$TOPIC"
```

#### IAM permissions (Kestra & GCS)

Grant Kestra the ability to see and pull messages, and grant GCS the ability to publish them.

```bash
# 1. Grant Kestra SA permissions to pull messages and view metadata
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:kestra-sa@${PROJECT}.iam.gserviceaccount.com" \
  --role="roles/pubsub.subscriber"

gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:kestra-sa@${PROJECT}.iam.gserviceaccount.com" \
  --role="roles/pubsub.viewer"

# 2. Grant the GCS Service Agent permission to publish to your topic
PROJECT_NUMBER=$(gcloud projects describe $PROJECT --format="value(projectNumber)")

gcloud pubsub topics add-iam-policy-binding "$TOPIC" --project "$PROJECT" \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gs-project-accounts.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"
```

#### Link GCS bucket to Pub/Sub

```bash
# Create the notification configuration (use topic in projects/.../topics/... form)
gsutil notification create -f json -t "projects/$PROJECT/topics/$TOPIC" "gs://$BUCKET"

# Verify the notification is active
gsutil notification list "gs://$BUCKET"
```

#### Kestra flow best practices (manual run safety)

To prevent `IllegalVariableEvaluationException` when clicking **Execute** manually (which lacks the trigger object), use the null-coalescing operator `??` in your flow YAML:

```yaml
tasks:
  - id: log_event
    type: io.kestra.plugin.core.debug.Return
    format: |
      Received Event:
      Bucket: {{ trigger.attributes.bucketId ?? 'manual-run' }}
      File:   {{ trigger.attributes.objectId ?? 'no-file' }}

errors:
  - id: on_error
    type: io.kestra.plugin.core.debug.Return
    format: |
      ERROR during RAW ingest:
      Bucket: {{ trigger.attributes.bucketId ?? 'N/A' }}
```

#### Create the event-driven flow

Use `flows/gcp.yellowcab/flows/3_5/event-file-ingest.yaml`. Replace project/dataset values.

This flow uses a `RealtimeTrigger` on the Pub/Sub subscription — whenever a file is uploaded to GCS, it automatically loads it into BigQuery.

#### End-to-end test

Do **not** click **Execute** in the UI. Instead, trigger the flow from your terminal:

```bash
# This upload will trigger the Pub/Sub message and start a Kestra execution automatically
gsutil cp yellow_tripdata_2025-03.parquet "gs://$BUCKET/"
```

Watch the execution appear in Kestra UI.

### How a real-time file event system works

Implementing an event-driven "file landing" approach means your workflow kicks off the exact moment a file hits your storage, rather than having a scheduler wake up every hour to check for new data.

Here is a breakdown of how this works in Kestra and how to achieve the same in the newly released Airflow 3.0 with Azure.

1. **The real-time concept (the "push" model)**  
   In a traditional setup, you use a Sensor (polling). In a real-time setup, you use a Trigger/Listener (event-based).

   *How it works:* Cloud Storage (Azure/GCP/AWS) emits an "Object Created" event.  
   *The glue:* This event is sent to a message queue (e.g. Azure Event Grid or GCP Pub/Sub).  
   *The action:* Your orchestrator (Kestra or Airflow 3) "subscribes" to that queue. When a message arrives, the workflow starts immediately.

2. **Kestra: RealtimeTrigger**  
   Kestra supports this out of the box. You define a `RealtimeTrigger` in your YAML:

   ```yaml
   triggers:
     - id: wait_for_azure_file
       type: io.kestra.plugin.azure.storage.blob.RealtimeTrigger
       endpoint: "{{ secret('AZURE_ENDPOINT') }}"
       container: "london-data-inbound"
   ```

   Kestra also supports triggering via Azure Event Hubs for high-scale events.

3. **Airflow 3.0: Asset-driven scheduling**  
   Before Airflow 3, you used a Poke sensor (expensive) or a Deferrable operator. Airflow 3.0 introduces AssetWatchers for efficiency.

   *Azure:* Set up Azure Event Grid to send an event to Azure Queue Storage or Event Hub whenever a blob is created.  
   *Airflow:* Use the Asset definition with a watcher:

   ```python
   from airflow.sdk.definitions.asset import Asset
   from airflow.providers.microsoft.azure.triggers.wasb import WasbBlobSensorTrigger

   my_file = Asset(
       "wasb://my-container/data.parquet",
       watchers=[
           WasbBlobSensorTrigger(
               container_name="my-container",
               blob_name="data.parquet",
               wasb_conn_id="azure_default"
           )
       ]
   )

   @dag(schedule=my_file)
   def process_blob():
       pass
   ```

4. **The shift: from "polling" to "listening"**  
   In Airflow 2.x, triggering when a file landed in GCS typically meant a `GCSObjectExistenceSensor` poking Google every few minutes.  
   Airflow 3.0 moves toward asset-driven scheduling: you define your data (e.g. GCS bucket or BigQuery table) as an Asset; Airflow "watches" it and starts the DAG when it changes.  
   Use GCP's push architecture: GCS Pub/Sub notification sends a small JSON message to a Pub/Sub topic on upload; your orchestrator subscribes to that topic (e.g. Kestra `RealtimeTrigger` or Airflow 3 AssetWatcher).

---

## Phase 4 — AI Agent & Dashboards (docs 4_1, 4_2)

Estimated time: 30–45 min

### Step 4.1 — Enable the Kestra AI Agent

#### Get a Gemini API key

Go to [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) and create an API key.

#### Update docker-compose.yml

Add the `ai:` block under `kestra:` in `KESTRA_CONFIGURATION`:

```yaml
kestra:
  ai:
    type: gemini
    gemini:
      api-key: YOUR-GEMINI-API-KEY
      model-name: gemini-2.5-flash
```

Restart Docker Compose.

#### Create the debug/demo flow

Use `flows/gcp.ecommerce/flows/4_1/debug-and-demo.yaml` in namespace `gcp.ecommerce`.

This flow demonstrates:

* Log levels (INFO, DEBUG, WARN, ERROR)
* Scheduled triggers (every 10 minutes)
* Intentional failure gate for Replay demo
* The AI agent can help debug failures in the UI

### Step 4.2 — Create a monitoring dashboard

Use `flows/gcp.ecommerce/dashboards/ecommerce-dashboard.yaml`.

In Kestra UI → Dashboards → Import/create the YAML.

The dashboard includes:

* Executions time series (last 7 days)
* Donut chart of execution states
* Next scheduled execution table
* Success rate KPI
* Executions per flow bar chart

---

## Summary of All GCP Resources Created

* **GCS Bucket:** 1 (with folders: `test/`, `yellow-cab/`, `yellow-cab-archive/`, `yc-retry/data/`, `yc-retry/archive/`, `yc-retry/errors/`)
* **BigQuery Datasets:** `kestra_test`, `raw`, `clean`, `YellowCab`, `yc_retry`
* **Service Account:** `kestra-sa` with BigQuery Admin + Storage Admin + Pub/Sub Subscriber roles
* **Pub/Sub:** 1 topic (`file-upload-events`) + 1 subscription (`file-upload-sub`)
* **APIs Enabled:** Cloud Storage, BigQuery, Pub/Sub

## Key Files Reference

* `docker-compose.yml` — Kestra + Postgres setup
* `.env_encoded` — Base64-encoded secrets (GCP key, GitHub token, Kestra creds)
* `helper_scripts/quick_base64_encode.py` — Offline base64 encoder
* `data-files/ecommerce.zip` — Ecommerce CSV dataset
* `data-files/taxi_zone_lookup.csv` — NYC taxi zone lookup table
* `data-files/retry-ok-file.csv` / `retry-error-file.csv` — Test files for error handling

## Cost Awareness

* BigQuery: Free tier covers 1 TB queries/month and 10 GB storage
* GCS: Free tier covers 5 GB storage
* Pub/Sub: Free tier covers 10 GB messages/month
* Stay within free tier by using small datasets and deleting resources when done
* Run `gcloud projects delete PROJECT_ID` when finished to avoid any charges
