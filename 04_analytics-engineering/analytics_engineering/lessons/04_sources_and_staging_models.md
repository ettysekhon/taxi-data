# Lesson 04: Sources & Staging Models

This is where you start building real dbt models. By the end of this lesson, you'll have defined where your raw data lives and created clean, typed staging models on top of it.

---

## What are sources?

Sources tell dbt where your raw data lives in the database. Instead of hard-coding table paths like `FROM prod.green_tripdata`, you declare them in YAML and reference them with the `{{ source() }}` function.

Why bother? Three reasons:

1. **Abstraction** — if your table moves or gets renamed, update one YAML file instead of every model
2. **Documentation** — column descriptions, freshness checks all live alongside the declaration
3. **Lineage** — dbt can trace the full path from raw source → final mart

---

## Hands-on: Define your sources

### Step 1: Create `models/staging/sources.yml`

Create a new file at `models/staging/sources.yml`:

```yaml
sources:
  - name: raw
    description: Raw taxi trip data from NYC TLC
    database: |
      {%- if target.type == 'bigquery' -%}
        {{ env_var('GCP_PROJECT_ID', 'please-add-your-gcp-project-id-here') }}
      {%- else -%}
        analytics_engineering
      {%- endif -%}
    schema: |
      {%- if target.type == 'bigquery' -%}
        nytaxi
      {%- else -%}
        prod
      {%- endif -%}
    freshness:
      warn_after: {count: 24, period: hour}
      error_after: {count: 48, period: hour}
    tables:
      - name: green_tripdata
        description: Raw green taxi trip records
        loaded_at_field: lpep_pickup_datetime
        columns:
          - name: vendorid
            description: "Taxi technology provider (1 = Creative Mobile Technologies, 2 = VeriFone Inc.)"
          - name: lpep_pickup_datetime
            description: Date and time when the meter was engaged
          - name: lpep_dropoff_datetime
            description: Date and time when the meter was disengaged
          - name: passenger_count
            description: Number of passengers in the vehicle
          - name: trip_distance
            description: Trip distance in miles
          - name: pulocationid
            description: TLC Taxi Zone where the meter was engaged
          - name: dolocationid
            description: TLC Taxi Zone where the meter was disengaged
          - name: payment_type
            description: "Payment method (1=Credit card, 2=Cash, 3=No charge, 4=Dispute, 5=Unknown, 6=Voided)"
          - name: fare_amount
            description: Time and distance fare
          - name: total_amount
            description: Total amount charged

      - name: yellow_tripdata
        description: Raw yellow taxi trip records
        loaded_at_field: tpep_pickup_datetime
        columns:
          - name: vendorid
            description: "Taxi technology provider (1 = Creative Mobile Technologies, 2 = VeriFone Inc.)"
          - name: tpep_pickup_datetime
            description: Date and time when the meter was engaged
          - name: tpep_dropoff_datetime
            description: Date and time when the meter was disengaged
          - name: passenger_count
            description: Number of passengers in the vehicle
          - name: trip_distance
            description: Trip distance in miles
          - name: pulocationid
            description: TLC Taxi Zone where the meter was engaged
          - name: dolocationid
            description: TLC Taxi Zone where the meter was disengaged
          - name: payment_type
            description: "Payment method (1=Credit card, 2=Cash, 3=No charge, 4=Dispute, 5=Unknown, 6=Voided)"
          - name: fare_amount
            description: Time and distance fare
          - name: total_amount
            description: Total amount charged
```

### Understanding the Jinja in database/schema

Notice the `{%- if target.type == 'bigquery' -%}` blocks. This makes the source definition work across multiple warehouses:

- If you're running against BigQuery, it uses your GCP project and `nytaxi` dataset
- If you're running against DuckDB, it uses the local database name and `prod` schema

This is a common pattern for projects that need to work in multiple environments.

### What the fields mean

| Field | Purpose |
|-------|---------|
| `name: raw` | Arbitrary label — used in `{{ source('raw', 'table_name') }}` |
| `database` | The database (DuckDB) or GCP project (BigQuery) |
| `schema` | The schema/dataset where raw tables live |
| `freshness` | How stale the data can be before warning/erroring |
| `loaded_at_field` | Which column to check for freshness |
| `tables` | List of tables in this source |

---

## Hands-on: Build staging models

Staging models do minimal cleaning: rename columns, cast types, filter garbage. They should be a **1:1 copy** of the source — same number of rows and columns (with one practical exception: filtering null vendor IDs).

### Step 2: Create `models/staging/stg_green_tripdata.sql`

```sql
with source as (
    select * from {{ source('raw', 'green_tripdata') }}
),

renamed as (
    select
        -- identifiers
        cast(vendorid as integer) as vendor_id,
        cast(ratecodeid as integer) as rate_code_id,
        cast(pulocationid as integer) as pickup_location_id,
        cast(dolocationid as integer) as dropoff_location_id,

        -- timestamps
        cast(lpep_pickup_datetime as timestamp) as pickup_datetime,
        cast(lpep_dropoff_datetime as timestamp) as dropoff_datetime,

        -- trip info
        cast(store_and_fwd_flag as string) as store_and_fwd_flag,
        cast(passenger_count as integer) as passenger_count,
        cast(trip_distance as numeric) as trip_distance,
        cast(trip_type as integer) as trip_type,

        -- payment info
        cast(fare_amount as numeric) as fare_amount,
        cast(extra as numeric) as extra,
        cast(mta_tax as numeric) as mta_tax,
        cast(tip_amount as numeric) as tip_amount,
        cast(tolls_amount as numeric) as tolls_amount,
        cast(ehail_fee as numeric) as ehail_fee,
        cast(improvement_surcharge as numeric) as improvement_surcharge,
        cast(total_amount as numeric) as total_amount,
        cast(payment_type as integer) as payment_type
    from source
    where vendorid is not null
)

select * from renamed

{% if target.name == 'dev' %}
where pickup_datetime >= '2019-01-01' and pickup_datetime < '2019-02-01'
{% endif %}
```

### What's happening here

1. **CTE pattern**: `source` → `renamed` → final select. This is the standard dbt staging pattern.
2. **`{{ source('raw', 'green_tripdata') }}`**: References the source defined in `sources.yml`. dbt resolves this to the actual table path at compile time.
3. **Explicit casting**: Don't trust the source types. Cast everything to what you actually want.
4. **Column renaming**: `vendorid` → `vendor_id`, `pulocationid` → `pickup_location_id`. Consistent, readable names.
5. **Column ordering**: IDs first, timestamps next, trip details, then payment info.
6. **Filtering null vendors**: A practical deviation from the 1:1 rule — these records are garbage.
7. **Dev sampling**: The `{% if target.name == 'dev' %}` block limits data to one month in dev. This makes development fast without processing all 50M+ rows.

### Step 3: Create `models/staging/stg_yellow_tripdata.sql`

Now do the same for yellow taxi data. The columns are almost identical, but note two differences:

- Timestamps are prefixed `tpep_` (Taxicab Passenger Enhancement Program) instead of `lpep_` (Licensed Passenger Enhancement Program)
- Yellow taxis don't have `trip_type` or `ehail_fee` columns

```sql
with source as (
    select * from {{ source('raw', 'yellow_tripdata') }}
),

renamed as (
    select
        -- identifiers
        cast(vendorid as integer) as vendor_id,
        cast(ratecodeid as integer) as rate_code_id,
        cast(pulocationid as integer) as pickup_location_id,
        cast(dolocationid as integer) as dropoff_location_id,

        -- timestamps
        cast(tpep_pickup_datetime as timestamp) as pickup_datetime,
        cast(tpep_dropoff_datetime as timestamp) as dropoff_datetime,

        -- trip info
        cast(store_and_fwd_flag as string) as store_and_fwd_flag,
        cast(passenger_count as integer) as passenger_count,
        cast(trip_distance as numeric) as trip_distance,

        -- payment info
        cast(fare_amount as numeric) as fare_amount,
        cast(extra as numeric) as extra,
        cast(mta_tax as numeric) as mta_tax,
        cast(tip_amount as numeric) as tip_amount,
        cast(tolls_amount as numeric) as tolls_amount,
        cast(improvement_surcharge as numeric) as improvement_surcharge,
        cast(total_amount as numeric) as total_amount,
        cast(payment_type as integer) as payment_type

    from source
    where vendorid is not null
)

select * from renamed

{% if target.name == 'dev' %}
where pickup_datetime >= '2019-01-01' and pickup_datetime < '2019-02-01'
{% endif %}
```

Notice yellow is **missing** `trip_type` and `ehail_fee`. We'll handle this mismatch in Lesson 05 when we union the two datasets.

---

## Verify it works

### Run the staging models

```bash
uv run dbt run --select models/staging
```

You should see both models build successfully. Since staging is materialized as views, this should be nearly instant.

### Inspect the compiled SQL

```bash
uv run dbt compile --select stg_green_tripdata
```

Then look at `target/compiled/.../stg_green_tripdata.sql`. You'll see the `{{ source() }}` call replaced with the actual table path. This is what dbt sends to DuckDB.

### Preview the data

```bash
uv run dbt show --select stg_green_tripdata --limit 5
```

This runs the model and shows you the first 5 rows without materializing anything.

---

## What you learned

- Sources are declared in YAML and referenced with `{{ source('name', 'table') }}`
- Staging models follow a standard CTE pattern: source → rename → select
- Always cast data types explicitly
- Use `{% if target.name == 'dev' %}` to limit data in development
- `dbt run --select` lets you build specific models instead of everything
- `dbt compile` and `dbt show` are fast feedback tools

---

**Next: [Lesson 05 — Intermediate Models](05_intermediate_models.md)**
