# Lesson 12: Homework

Time to test what you've learned. These questions come from the [Module 4 Homework](../../homework.md) of the Data Engineering Zoomcamp. Questions 1-5 use the project you've already built. Question 6 asks you to extend it with a new dataset.

---

## Before you start

Make sure you've built the full project against the prod target:

```bash
uv run dbt seed --target prod
uv run dbt build --target prod
```

After a successful build you should have `fct_trips`, `dim_zones`, and `fct_monthly_zone_revenue` in the `prod` schema.

---

## Question 1: dbt Lineage and Execution

Given this project structure:

```text
models/
├── staging/
│   ├── stg_green_tripdata.sql
│   └── stg_yellow_tripdata.sql
└── intermediate/
    └── int_trips_unioned.sql (depends on stg_green_tripdata & stg_yellow_tripdata)
```

If you run `uv run dbt run --select int_trips_unioned`, what models will be built?

- `stg_green_tripdata`, `stg_yellow_tripdata`, and `int_trips_unioned` (upstream dependencies)
- Any model with upstream and downstream dependencies to `int_trips_unioned`
- `int_trips_unioned` only
- `int_trips_unioned`, `int_trips`, and `fct_trips` (downstream dependencies)

**Hint:** Review [Lesson 11](11_commands_reference.md) — specifically the `--select` flag and the `+` graph operator. What does `--select` do *without* the `+` prefix?

---

## Question 2: dbt Tests

You've configured a generic test like this in your `schema.yml`:

```yaml
columns:
  - name: payment_type
    data_tests:
      - accepted_values:
          arguments:
            values: [1, 2, 3, 4, 5]
            quote: false
```

Your model `fct_trips` has been running successfully for months. A new value `6` now appears in the source data. What happens when you run `uv run dbt test --select fct_trips`?

- dbt will skip the test because the model didn't change
- dbt will fail the test, returning a non-zero exit code
- dbt will pass the test with a warning about the new value
- dbt will update the configuration to include the new value

**Hint:** Review [Lesson 08](08_tests_and_data_quality.md) — how do `accepted_values` tests work? Does dbt auto-update YAML?

---

## Question 3: Counting Records in `fct_monthly_zone_revenue`

Query the `fct_monthly_zone_revenue` model in your prod schema:

```sql
SELECT count(*) FROM prod.fct_monthly_zone_revenue;
```

What is the count of records?

- 12,998
- 14,120
- 12,184
- 15,421

**How to query:** You can use the DuckDB CLI (`duckdb analytics_engineering.duckdb`) or `uv run dbt show`:

```bash
uv run dbt show --inline "select count(*) as cnt from {{ ref('fct_monthly_zone_revenue') }}" --target prod
```

---

## Question 4: Best Performing Zone for Green Taxis (2020)

Using `fct_monthly_zone_revenue`, find the pickup zone with the **highest total revenue** (`revenue_monthly_total_amount`) for **Green** taxi trips in 2020.

```sql
SELECT
    pickup_zone,
    sum(revenue_monthly_total_amount) as total_revenue
FROM prod.fct_monthly_zone_revenue
WHERE service_type = 'Green'
  AND revenue_month >= '2020-01-01'
  AND revenue_month < '2021-01-01'
GROUP BY pickup_zone
ORDER BY total_revenue DESC
LIMIT 5;
```

Which zone had the highest revenue?

- East Harlem North
- Morningside Heights
- East Harlem South
- Washington Heights South

---

## Question 5: Green Taxi Trip Counts (October 2019)

What is the **total number of trips** (`total_monthly_trips`) for Green taxis in October 2019?

```sql
SELECT sum(total_monthly_trips) as total_trips
FROM prod.fct_monthly_zone_revenue
WHERE service_type = 'Green'
  AND revenue_month = '2019-10-01';
```

- 500,234
- 350,891
- 384,624
- 421,509

---

## Question 6: Build a Staging Model for FHV Data

This is the hands-on challenge. You need to create a staging model for **For-Hire Vehicle (FHV)** trip data for 2019.

### What is FHV data?

FHV stands for For-Hire Vehicle. These are services like Uber, Lyft, and other livery/black car services in NYC. The FHV dataset has a very different schema from yellow/green taxis — no fare amounts, no payment types. Instead it has dispatching base numbers and a shared ride flag.

### The FHV schema

| Raw column | Type | Description |
|-----------|------|-------------|
| `dispatching_base_num` | string | TLC base license number of the dispatching base |
| `pickup_datetime` | timestamp | Pickup date and time |
| `dropoff_datetime` | timestamp | Dropoff date and time |
| `PUlocationID` | integer | TLC Taxi Zone where the trip started |
| `DOlocationID` | integer | TLC Taxi Zone where the trip ended |
| `SR_Flag` | integer | Shared ride flag (1 = shared, null = not shared) |
| `Affiliated_base_number` | string | TLC base license number of the affiliated base |

### Step 1: Ingest the FHV data

The ingestion script already supports FHV — just pass the `--fhv` flag:

```bash
python scripts/ingest_data.py --fhv
```

This downloads all 12 months of 2019 FHV data and loads it into `prod.fhv_tripdata`.

### Step 2: Build the staging model

The source definition and staging model are already in the project as your answer key:

- Source: `models/staging/sources.yml` (look for `fhv_tripdata`)
- Model: `models/staging/stg_fhv_tripdata.sql`
- Tests: `models/staging/schema.yml` (look for `stg_fhv_tripdata`)

**The challenge:** Before looking at the answer key, try building `stg_fhv_tripdata.sql` yourself. Apply the same patterns you learned in [Lesson 04](04_sources_and_staging_models.md):

1. Pull from `{{ source('raw', 'fhv_tripdata') }}`
2. Rename columns to match your project's conventions (e.g., `PUlocationID` to `pickup_location_id`)
3. Cast data types explicitly
4. Filter out records where `dispatching_base_num IS NULL`
5. Add a dev environment filter on `pickup_datetime`

### Step 3: Build and count

```bash
uv run dbt build --select stg_fhv_tripdata --target prod
```

Then query the row count:

```sql
SELECT count(*) FROM prod.stg_fhv_tripdata;
```

What is the count of records?

- 42,084,899
- 43,244,693
- 22,998,722
- 44,112,187

**Important:** Make sure you're running against `--target prod` (no date filter) and that you're filtering `WHERE dispatching_base_num IS NOT NULL`.
