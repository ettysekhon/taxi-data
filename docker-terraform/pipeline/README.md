# Docker & Terraform Pipeline

---

## Part 1: Docker Basics

### Step 1.1: Test Docker is working

```bash
docker run hello-world
```

### Step 1.2: Run Python container with bash

```bash
docker run -it --rm --entrypoint=bash python:3.13
```

Inside the container:

```bash
pip --version
python -V
exit
```

---

## Part 2: Set Up Project Directory

### Step 2.1: Create project folder

```bash
mkdir pipeline
cd pipeline
```

### Step 2.2: Initialize Python project with uv

```bash
pip install uv
uv init --python=3.13
```

### Step 2.3: Add dependencies

```bash
uv add pandas pyarrow sqlalchemy psycopg2-binary click tqdm
uv add --dev pgcli jupyter
```

---

## Part 3: Run PostgreSQL with Docker

### Step 3.1: Create docker-compose.yaml

```yaml
services:
  pgdatabase:
    image: postgres:18
    environment:
      POSTGRES_USER: "root"
      POSTGRES_PASSWORD: "root"
      POSTGRES_DB: "ny_taxi"
    volumes:
      - ny_taxi_postgres_data:/var/lib/postgresql
    ports:
      - "5432:5432"

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: "admin@admin.com"
      PGADMIN_DEFAULT_PASSWORD: "root"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    ports:
      - "8085:80"

volumes:
  ny_taxi_postgres_data:
  pgadmin_data:
```

### Step 3.2: Start containers

```bash
docker compose up -d
```

### Step 3.3: Verify PostgreSQL is running

```bash
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi
```

Password: `root`

Test inside pgcli:

```sql
\dt
\q
```

### Step 3.4: Access pgAdmin

1. Open browser: <http://localhost:8085>
2. Login: `admin@admin.com` / `root`
3. Right-click "Servers" → Register → Server
4. General tab → Name: `Docker`
5. Connection tab:
   - Host: `pgdatabase`
   - Port: `5432`
   - Username: `root`
   - Password: `root`
6. Save

---

## Part 4: Data Ingestion Script

### Step 4.1: Create ingest_data.py

```python
#!/usr/bin/env python
import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

@click.command()
@click.option('--pg-user', default='root')
@click.option('--pg-pass', default='root')
@click.option('--pg-host', default='localhost')
@click.option('--pg-port', default=5432, type=int)
@click.option('--pg-db', default='ny_taxi')
@click.option('--year', default=2021, type=int)
@click.option('--month', default=1, type=int)
@click.option('--target-table', default='yellow_taxi_data')
@click.option('--chunksize', default=100000, type=int)
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, target_table, chunksize):
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow'
    url = f'{prefix}/yellow_tripdata_{year}-{month:02d}.csv.gz'

    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize,
    )

    first = True
    for df_chunk in tqdm(df_iter):
        if first:
            df_chunk.head(0).to_sql(name=target_table, con=engine, if_exists='replace')
            first = False
        df_chunk.to_sql(name=target_table, con=engine, if_exists='append')

if __name__ == '__main__':
    run()
```

### Step 4.2: Run ingestion locally

```bash
uv run python ingest_data.py \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=localhost \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --target-table=yellow_taxi_trips
```

### Step 4.3: Verify data in pgcli

```bash
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi
```

```sql
SELECT COUNT(*) FROM yellow_taxi_trips;
\q
```

---

## Part 5: Dockerize the Ingestion Script

### Step 5.1: Create Dockerfile

```dockerfile
FROM python:3.13.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /code
ENV PATH="/code/.venv/bin:$PATH"

COPY pyproject.toml .python-version uv.lock ./
RUN uv sync --locked

COPY ingest_data.py .

ENTRYPOINT ["python", "ingest_data.py"]
```

### Step 5.2: Build the image

```bash
docker build -t taxi_ingest:v001 .
```

### Step 5.3: Get the docker-compose network name

```bash
docker network ls
```

Look for `pipeline_default` (or `<foldername>_default`).

### Step 5.4: Run containerized ingestion

```bash
docker run -it --rm \
  --network=pipeline_default \
  taxi_ingest:v001 \
    --pg-user=root \
    --pg-pass=root \
    --pg-host=pgdatabase \
    --pg-port=5432 \
    --pg-db=ny_taxi \
    --target-table=yellow_taxi_trips
```

Note: `--pg-host=pgdatabase` uses the service name from docker-compose.

---

## Part 6: SQL Queries

### Step 6.1: Download zones data

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

### Step 6.2: Load zones into Postgres

Option A - Using Python (run this in the pipeline directory):

```bash
uv run python -c "
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')
df = pd.read_csv('taxi_zone_lookup.csv')
df.to_sql('zones', engine, if_exists='replace', index=False)
print(f'Loaded {len(df)} zones')
"
```

Option B - Using pgcli:

```bash
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi
```

Inside pgcli:

```sql
CREATE TABLE zones (
    "LocationID" INTEGER,
    "Borough" TEXT,
    "Zone" TEXT,
    "service_zone" TEXT
);

\copy zones FROM 'taxi_zone_lookup.csv' WITH (FORMAT csv, HEADER true);

SELECT COUNT(*) FROM zones;
\q
```

### Step 6.3: Verify zones loaded

```bash
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi
```

```sql
SELECT * FROM zones LIMIT 5;
\q
```

### Step 6.4: Example queries in pgcli/pgAdmin

**Count records:**

```sql
SELECT COUNT(*) FROM yellow_taxi_trips;
```

**Join with zones:**

```sql
SELECT
    tpep_pickup_datetime,
    total_amount,
    CONCAT(zpu."Borough", ' | ', zpu."Zone") AS pickup_loc,
    CONCAT(zdo."Borough", ' | ', zdo."Zone") AS dropoff_loc
FROM
    yellow_taxi_trips t
JOIN zones zpu ON t."PULocationID" = zpu."LocationID"
JOIN zones zdo ON t."DOLocationID" = zdo."LocationID"
LIMIT 10;
```

**Group by day:**

```sql
SELECT
    CAST(tpep_pickup_datetime AS DATE) AS day,
    COUNT(*) AS trips
FROM yellow_taxi_trips
GROUP BY 1
ORDER BY 1;
```

**Aggregations:**

```sql
SELECT
    CAST(tpep_pickup_datetime AS DATE) AS day,
    COUNT(*) AS trips,
    MAX(trip_distance) AS max_distance,
    SUM(total_amount) AS total_revenue
FROM yellow_taxi_trips
GROUP BY 1
ORDER BY total_revenue DESC
LIMIT 10;
```

---

## Part 7: Terraform (GCP)

### Step 7.1: GCP Initial Setup

1. Create GCP account: <https://console.cloud.google.com/>
2. Create a new project (e.g., "dtc-de-course")
3. Note down your **Project ID** (not the project name)

### Step 7.2: Create Service Account

1. Go to **IAM & Admin** → **Service Accounts**: <https://console.cloud.google.com/iam-admin/serviceaccounts>
2. Click **Create Service Account**
3. Name: `terraform-runner` (or any name)
4. Click **Create and Continue**
5. Skip the optional steps, click **Done**

### Step 7.3: Download Service Account Key

1. Click on your new service account
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Select **JSON** → **Create**
5. Save the downloaded file

### Step 7.4: Set Up Keys Directory

```bash
mkdir -p terraform/keys
mv ~/Downloads/<your-key-file>.json terraform/keys/my-creds.json
```

### Step 7.5: Add IAM Roles to Service Account

1. Go to **IAM & Admin** → **IAM**: <https://console.cloud.google.com/iam-admin/iam>
2. Find your service account, click the **pencil icon** (Edit)
3. Click **Add Another Role** and add these roles:
   - **Storage Admin**
   - **Storage Object Admin**
   - **BigQuery Admin**
4. Click **Save**

### Step 7.6: Enable Required APIs

Enable these APIs for your project:

1. IAM API: <https://console.cloud.google.com/apis/library/iam.googleapis.com>
2. IAM Credentials API: <https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com>

Click **Enable** on each page.

### Step 7.7: Set Environment Variable

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/terraform/keys/my-creds.json"
```

Add to your `~/.zshrc` or `~/.bashrc` to make it permanent:

```bash
echo 'export GOOGLE_APPLICATION_CREDENTIALS="<full-path-to>/keys/my-creds.json"' >> ~/.zshrc
source ~/.zshrc
```

### Step 7.8: Authenticate with GCP

```bash
gcloud auth application-default login
```

### Step 7.9: Create Terraform Directory

```bash
mkdir -p terraform
cd terraform
```

### Step 7.10: Create variables.tf

```hcl
variable "credentials" {
  description = "Path to service account JSON"
  default     = "./keys/my-creds.json"
}

variable "project" {
  description = "GCP Project ID"
  default     = "<YOUR-PROJECT-ID>"
}

variable "region" {
  default = "us-central1"
}

variable "location" {
  default = "US"
}

variable "bq_dataset_name" {
  default = "demo_dataset"
}

variable "gcs_bucket_name" {
  description = "Must be globally unique"
  default     = "<YOUR-UNIQUE-BUCKET-NAME>"
}
```

**Important:** Replace:

- `<YOUR-PROJECT-ID>` with your actual GCP project ID
- `<YOUR-UNIQUE-BUCKET-NAME>` with a globally unique name (e.g., `dtc-de-bucket-12345`)

### Step 7.11: Create main.tf

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project
  region      = var.region
}

resource "google_storage_bucket" "demo-bucket" {
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.location
}
```

### Step 7.12: Create .gitignore for Terraform

```bash
cat << 'EOF' > .gitignore
# Local .terraform directories
**/.terraform/*

# .tfstate files
*.tfstate
*.tfstate.*

# Crash log files
crash.log
crash.*.log

# Exclude all .tfvars files, which are likely to contain sensitive data
*.tfvars
*.tfvars.json

# Ignore override files
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# Ignore CLI configuration files
.terraformrc
terraform.rc

# Ignore credentials
keys/
*.json
EOF
```

### Step 7.13: Initialize Terraform

```bash
terraform init
```

Expected output: "Terraform has been successfully initialized!"

### Step 7.14: Preview Changes

```bash
terraform plan
```

Review the output - it should show 2 resources to add (bucket + dataset).

### Step 7.15: Apply Changes

```bash
terraform apply
```

Type `yes` when prompted.

### Step 7.16: Verify in GCP Console

1. Check bucket: <https://console.cloud.google.com/storage/browser>
2. Check BigQuery dataset: <https://console.cloud.google.com/bigquery>

### Step 7.17: Destroy Resources (when done)

```bash
terraform destroy
```

Type `yes` when prompted.

---

### Fallback: If Service Account Key Creation is Blocked

If your organization blocks direct key creation, use impersonation:

**Step A:** Give yourself token creator role:

```bash
gcloud iam service-accounts add-iam-policy-binding \
    <SERVICE_ACCOUNT_EMAIL> \
    --member="user:<YOUR_EMAIL>@gmail.com" \
    --role="roles/iam.serviceAccountTokenCreator"
```

**Step B:** Modify main.tf to use impersonation:

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}

# Primary provider using ADC
provider "google" {
  project = var.project
  region  = var.region
}

# Get temporary token for service account
data "google_service_account_access_token" "default" {
  provider               = google
  target_service_account = "<SERVICE_ACCOUNT_EMAIL>"
  scopes                 = ["https://www.googleapis.com/auth/cloud-platform"]
  lifetime               = "3600s"
}

# Impersonated provider for actual resource creation
provider "google" {
  alias        = "impersonated"
  access_token = data.google_service_account_access_token.default.access_token
  project      = var.project
  region       = var.region
}

resource "google_storage_bucket" "demo-bucket" {
  provider      = google.impersonated
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true
}

resource "google_bigquery_dataset" "demo_dataset" {
  provider   = google.impersonated
  dataset_id = var.bq_dataset_name
  location   = var.location
}
```

---

## Part 8: Cleanup

### Step 8.1: Stop docker-compose

```bash
docker compose down
```

### Step 8.2: Remove volumes (optional)

```bash
docker compose down -v
```

### Step 8.3: Remove images (optional)

```bash
docker rmi taxi_ingest:v001
docker image prune -a
```

### Step 8.4: Full cleanup (nuclear option)

```bash
docker system prune -a --volumes
```

---

## Quick Reference

### Docker Commands

| Task | Command |
| ---- | ------- |
| Start services | `docker compose up -d` |
| Stop services | `docker compose down` |
| Stop + remove volumes | `docker compose down -v` |
| View logs | `docker compose logs` |
| Build image | `docker build -t taxi_ingest:v001 .` |
| List containers | `docker ps -a` |
| List images | `docker images` |
| List networks | `docker network ls` |

### Database Commands

| Task | Command |
| ---- | ------- |
| Connect to Postgres | `uv run pgcli -h localhost -p 5432 -u root -d ny_taxi` |
| Open pgAdmin | <http://localhost:8085> |

### Terraform Commands

| Task | Command |
| ---- | ------- |
| Initialize | `terraform init` |
| Preview changes | `terraform plan` |
| Apply changes | `terraform apply` |
| Apply (no prompt) | `terraform apply -auto-approve` |
| Destroy resources | `terraform destroy` |
| Format files | `terraform fmt` |
| Validate config | `terraform validate` |
| Show state | `terraform show` |

### GCP Commands

| Task | Command |
| ---- | ------- |
| Authenticate | `gcloud auth application-default login` |
| Set project | `gcloud config set project <PROJECT_ID>` |
| List projects | `gcloud projects list` |
