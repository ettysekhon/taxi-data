# Learning dlt (data load tool)

Personal step-by-step guide to learning dlt core — from zero to a working pipeline.

## What is dlt

dlt is the **E** and **L** in ELT. It extracts data from sources (APIs, files, databases) and loads it into destinations (DuckDB, BigQuery, Snowflake) with automatic schema inference, normalisation, and incremental loading. You write Python; dlt handles the plumbing.

**dbt comparison:** dbt does the T (transform). dlt does the E+L. They're complementary — dlt loads raw data, dbt transforms it.

## Setup

```bash
# From this directory
cd workshops/dlt

# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Init project and install deps
uv init --no-readme
uv add "dlt[duckdb]"

# Verify
uv run python -c "import dlt; print(dlt.__version__)"
```

### Optional: dlt MCP for Cursor

Settings → Tools & MCP → New MCP Server:

```json
{
  "mcpServers": {
    "dlt": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "dlt[duckdb]",
        "--with",
        "dlt-mcp[search]",
        "python",
        "-m",
        "dlt_mcp"
      ]
    }
  }
}
```

### Optional: Dashboard and visualisation

```bash
uv add "dlt[workspace]" "ibis-framework[duckdb]" marimo altair
```

---

## Step 1: Hello World — list to DuckDB

Simplest possible pipeline. Understand `dlt.pipeline` and `pipeline.run`.

```python
# hello_dlt.py
import dlt

data = [
    {"name": "Kings Cross", "zone": 1, "lines": ["Northern", "Piccadilly", "Victoria"]},
    {"name": "Bank", "zone": 1, "lines": ["Central", "Northern", "Waterloo & City"]},
    {"name": "Stratford", "zone": 3, "lines": ["Central", "Jubilee"]},
]

pipeline = dlt.pipeline(
    pipeline_name="hello_pipeline",
    destination="duckdb",
    dataset_name="tube_data",
)

load_info = pipeline.run(data, table_name="stations")
print(load_info)
```

```bash
uv run python hello_dlt.py
```

**What to notice:**

- dlt created a DuckDB file automatically
- It inferred the schema from your Python dicts
- Nested lists (`lines`) get normalised into a separate child table (`stations__lines`)
- Run it twice — rows double (default `write_disposition` is `append`)

**Inspect it:**

```bash
uv run dlt pipeline hello_pipeline show
```

Or query directly:

```python
# query.py
import dlt

pipeline = dlt.attach("hello_pipeline")
with pipeline.sql_client() as client:
    result = client.execute_sql("SELECT * FROM tube_data.stations")
    for row in result:
        print(row)
```

### Key concepts learned

| Concept             | What it does                                             |
| ------------------- | -------------------------------------------------------- |
| `dlt.pipeline()`    | Creates a pipeline with a name, destination, and dataset |
| `pipeline.run()`    | Extracts, normalises, loads in one call                  |
| `write_disposition` | `append` (default), `replace`, or `merge`                |
| Normalisation       | Nested JSON → flat relational tables automatically       |

---

## Step 2: REST API source — TFL Bike Points

Use dlt's built-in `rest_api_source` to hit a real API. TFL is free, no auth needed.

```python
# tfl_bikes_pipeline.py
import dlt
from dlt.sources.rest_api import rest_api_source

source = rest_api_source({
    "client": {
        "base_url": "https://api.tfl.gov.uk",
    },
    "resource_defaults": {
        "primary_key": "id",
        "write_disposition": "replace",
    },
    "resources": [
        {
            "name": "bike_points",
            "endpoint": {
                "path": "BikePoint",
            },
        },
    ],
})

pipeline = dlt.pipeline(
    pipeline_name="tfl_pipeline",
    destination="duckdb",
    dataset_name="tfl_data",
)

load_info = pipeline.run(source)
print(load_info)
```

```bash
uv run python tfl_bikes_pipeline.py
```

**What to notice:**

- `rest_api_source` handles HTTP, JSON parsing, schema inference
- `primary_key: "id"` enables deduplication if you switch to `merge`
- `write_disposition: "replace"` drops and recreates each run (good for reference data)
- TFL returns ~800 bike points with nested `additionalProperties` — dlt flattens them

**Query it:**

```bash
uv run dlt pipeline tfl_pipeline show
```

### Key concepts learned

| Concept                      | What it does                                                     |
| ---------------------------- | ---------------------------------------------------------------- |
| `rest_api_source`            | Declarative REST API extraction (config-driven, not code-driven) |
| `client.base_url`            | Shared base URL across all resources                             |
| `primary_key`                | Used for merge/dedup; also tracked in schema metadata            |
| `write_disposition: replace` | Full refresh — good for small reference datasets                 |

---

## Step 3: Pagination

Most APIs paginate. dlt has built-in paginators.

```python
# tfl_air_quality_pipeline.py
import dlt
from dlt.sources.rest_api import rest_api_source

source = rest_api_source({
    "client": {
        "base_url": "https://api.tfl.gov.uk",
    },
    "resources": [
        {
            "name": "air_quality",
            "endpoint": {
                "path": "AirQuality",
                "data_selector": "currentForecast",
            },
            "write_disposition": "replace",
        },
    ],
})

pipeline = dlt.pipeline(
    pipeline_name="tfl_air_pipeline",
    destination="duckdb",
    dataset_name="tfl_air_data",
)

load_info = pipeline.run(source)
print(load_info)
```

For APIs with offset/page pagination (e.g., the homework NYC taxi API):

```python
"endpoint": {
    "path": "search.json",
    "params": {"q": "london", "limit": 100},
    "data_selector": "docs",
    "paginator": {
        "type": "offset",
        "limit": 100,
        "offset_param": "offset",
        "limit_param": "limit",
        "total_path": "numFound",
    },
},
```

### Paginator types

| Type          | Use when                                          |
| ------------- | ------------------------------------------------- |
| `offset`      | API uses `offset` + `limit` params                |
| `page_number` | API uses `page=1`, `page=2`, etc.                 |
| `cursor`      | API returns a `next_cursor` token                 |
| `header_link` | API puts next URL in `Link` header (GitHub style) |
| `json_link`   | API puts next URL in the response body            |
| `auto`        | Let dlt guess (works surprisingly often)          |

---

## Step 4: Incremental loading

Don't re-fetch everything every run. Use `incremental` to track what you've already loaded.

```python
"resources": [
    {
        "name": "trips",
        "endpoint": {
            "path": "trips",
            "incremental": {
                "cursor_path": "pickup_datetime",    # field in each record
                "initial_value": "2024-01-01T00:00:00",
            },
        },
        "write_disposition": "append",
    },
]
```

**How it works:**

1. First run: loads everything from `initial_value` onwards
2. dlt stores the max `pickup_datetime` value it saw in pipeline state
3. Next run: only fetches records after that value
4. Combined with `append`, you get incremental loading without duplicates

**Alternative — `merge` for upserts:**

```python
"write_disposition": "merge",
"primary_key": "trip_id",
```

This inserts new rows and updates existing ones (matched by `trip_id`).

---

## Step 5: Custom Python source (generator)

When `rest_api_source` doesn't fit (auth flows, complex logic, non-REST sources):

```python
import dlt
import requests

@dlt.resource(write_disposition="append", primary_key="id")
def tfl_disruptions():
    """Yield current TFL disruptions."""
    url = "https://api.tfl.gov.uk/Line/Mode/tube/Disruption"
    response = requests.get(url)
    response.raise_for_status()
    yield from response.json()

pipeline = dlt.pipeline(
    pipeline_name="disruptions_pipeline",
    destination="duckdb",
    dataset_name="tfl_disruptions",
)

load_info = pipeline.run(tfl_disruptions)
print(load_info)
```

**Key difference:** With `@dlt.resource`, you write the HTTP calls yourself but dlt still handles normalisation, schema inference, and loading.

---

## Step 6: Inspect and query

### Dashboard

```bash
uv run dlt pipeline <pipeline_name> show
```

### SQL client

```python
pipeline = dlt.attach("tfl_pipeline")
with pipeline.sql_client() as client:
    rows = client.execute_sql("SELECT id, commonName FROM tfl_data.bike_points LIMIT 10")
    for row in rows:
        print(row)
```

### marimo notebook (optional)

```python
# analysis.py
import marimo
app = marimo.App()

@app.cell
def _():
    import dlt, ibis
    pipeline = dlt.attach("tfl_pipeline")
    con = pipeline.dataset().ibis()
    return con

@app.cell
def _(con):
    con.table("bike_points").count().to_pandas()

if __name__ == "__main__":
    app.run()
```

```bash
uv run marimo edit analysis.py
```

---

## Existing files in this directory

| File                          | What it is                                                 |
| ----------------------------- | ---------------------------------------------------------- |
| `open_library_pipeline.py`    | Working pipeline — Open Library Search API (from workshop) |
| `analysis.py`                 | marimo notebook — Harry Potter book analysis               |
| `dlt_homework.md`             | Homework — NYC taxi data from custom paginated API         |
| `dlt_Pipeline_Overview.ipynb` | Colab notebook — dlt concepts walkthrough                  |
| `pyproject.toml`              | Dependencies                                               |

---

## Homework

See [dlt_homework.md](dlt_homework.md) — build a pipeline for NYC taxi data from a paginated API, then answer 3 questions about the loaded data.

---

## Gaps to revisit

- [ ] **Incremental loading in practice** — haven't built a pipeline with `merge` or `incremental` cursor on a real dataset yet
- [ ] **Schema evolution** — what happens when the API adds/removes fields between runs?
- [ ] **Schema contracts** — `dlt.resource(schema_contract="freeze")` to lock down schemas in prod
- [ ] **Error handling** — retries, dead letter queues, partial loads
- [ ] **Secrets management** — `secrets.toml` vs env vars vs vault for API keys
- [ ] **Deployment** — running dlt on Airflow/Dagster/GitHub Actions (not just local)
- [ ] **Performance** — parallelism, file-based staging for large datasets
- [ ] **dlt + dbt integration** — dlt loads raw, dbt transforms; how to wire them together
- [ ] **TFL API deeper dive** — authenticated endpoints (journey planner, Oyster data) need an app key

## Quick reference

```bash
# Create pipeline
uv run python my_pipeline.py

# Inspect
uv run dlt pipeline <name> show
uv run dlt pipeline <name> info
uv run dlt pipeline <name> schema

# Drop and restart
uv run dlt pipeline <name> drop

# List all local pipelines
uv run dlt pipeline --list
```

## Resources

| Resource            | Link                                                                                                                       |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| dlt docs            | [dlthub.com/docs](https://dlthub.com/docs)                                                                                 |
| REST API source     | [dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api) |
| Incremental loading | [dlthub.com/docs/general-usage/incremental-loading](https://dlthub.com/docs/general-usage/incremental-loading)             |
| Schema contracts    | [dlthub.com/docs/general-usage/schema-contracts](https://dlthub.com/docs/general-usage/schema-contracts)                   |
| TFL API docs        | [api.tfl.gov.uk](https://api.tfl.gov.uk)                                                                                   |
| dlt + dbt           | [dlthub.com/docs/dlt-ecosystem/transformations/dbt](https://dlthub.com/docs/dlt-ecosystem/transformations/dbt)            ) |
| TFL API docs | [api.tfl.gov.uk](https://api.tfl.gov.uk) |
| dlt + dbt | [dlthub.com/docs/dlt-ecosystem/transformations/dbt](https://dlthub.com/docs/dlt-ecosystem/transformations/dbt) |
