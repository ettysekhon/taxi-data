# Lesson 07: Marts — Fact & Dimension Tables

This is where everything comes together. The marts layer contains the final, consumption-ready tables that business users, BI tools, and dashboards will query. We're building a **star schema**: fact tables (events) surrounded by dimension tables (context).

---

## What goes in marts?

If it's in `models/marts/`, it's ready for end users. Only marts tables should be exposed to BI tools and analysts. Everything upstream (staging, intermediate) is internal plumbing.

We'll build:

- **`dim_zones`** — dimension table for taxi zones (from seed)
- **`dim_vendors`** — dimension table for taxi vendors (from macro)
- **`fct_trips`** — fact table with one row per trip (from intermediate)
- **`fct_monthly_zone_revenue`** — reporting aggregate for dashboards

---

## Hands-on: Build dimension tables

### Step 1: Create `models/marts/dim_zones.sql`

The simplest possible model — a pass-through from the seed with renamed columns:

```sql
select
    locationid as location_id,
    borough,
    zone,
    service_zone
from {{ ref('taxi_zone_lookup') }}
```

That's it. Why have a model at all when it's just selecting from a seed? Because having it as a model:

- Gives you a place to add future logic (calculated fields, filtering)
- Keeps the naming convention consistent (`dim_` prefix)
- Means downstream models reference `dim_zones` instead of the raw seed

### Step 2: Create `models/marts/dim_vendors.sql`

This model uses the macro from Lesson 06:

```sql
with trips as (
    select * from {{ ref('fct_trips') }}
),

vendors as (
    select distinct
        vendor_id,
        {{ get_vendor_data('vendor_id') }} as vendor_name
    from trips
)

select * from vendors
```

Note this references `fct_trips` — a model we haven't created yet. uv run dbt handles circular-looking references just fine as long as there's no actual cycle. In this case, `dim_vendors` depends on `fct_trips`, not the other way around.

---

## Hands-on: Build the fact table

### Step 3: Create `models/marts/fct_trips.sql`

This is the core table — one row per taxi trip, enriched with zone information. It uses an **incremental** materialization to handle the large dataset efficiently.

```sql
{{
  config(
    materialized='incremental',
    unique_key='trip_id',
    incremental_strategy='merge',
    on_schema_change='append_new_columns'
  )
}}

select
    trips.trip_id,
    trips.vendor_id,
    trips.service_type,
    trips.rate_code_id,

    trips.pickup_location_id,
    pz.borough as pickup_borough,
    pz.zone as pickup_zone,
    trips.dropoff_location_id,
    dz.borough as dropoff_borough,
    dz.zone as dropoff_zone,

    trips.pickup_datetime,
    trips.dropoff_datetime,
    trips.store_and_fwd_flag,

    trips.passenger_count,
    trips.trip_distance,
    trips.trip_type,
    {{ get_trip_duration_minutes('trips.pickup_datetime', 'trips.dropoff_datetime') }} as trip_duration_minutes,

    trips.fare_amount,
    trips.extra,
    trips.mta_tax,
    trips.tip_amount,
    trips.tolls_amount,
    trips.ehail_fee,
    trips.improvement_surcharge,
    trips.total_amount,
    trips.payment_type,
    trips.payment_type_description

from {{ ref('int_trips') }} as trips
left join {{ ref('dim_zones') }} as pz
    on trips.pickup_location_id = pz.location_id
left join {{ ref('dim_zones') }} as dz
    on trips.dropoff_location_id = dz.location_id

{% if is_incremental() %}
  where trips.pickup_datetime > (select max(pickup_datetime) from {{ this }})
{% endif %}
```

### What's happening

1. **Incremental materialization** — the `config()` block at the top tells uv run dbt this is incremental. Instead of rebuilding the entire table every time, it only processes new rows.

2. **`{{ this }}`** — a special uv run dbt variable that refers to the current model's existing table. Used in the `is_incremental()` block to find the max date already loaded.

3. **`is_incremental()`** — a Jinja function that returns true only when:
   - The model is configured as incremental
   - The target table already exists
   - `--full-refresh` was NOT passed

4. **Zone enrichment via LEFT JOIN** — we join `dim_zones` twice (once for pickup, once for dropoff) to add human-readable borough and zone names. LEFT JOIN preserves all trips even if zone info is missing.

5. **Trip duration macro** — `{{ get_trip_duration_minutes(...) }}` uses the cross-database macro from Lesson 06.

### Why incremental?

The taxi dataset has tens of millions of rows. Rebuilding the entire table every time would be slow and expensive. Incremental processing means:

- **First run**: full table build (may take several minutes)
- **Subsequent runs**: only new rows get processed (much faster)
- **Full refresh**: `uv run dbt run --full-refresh --select fct_trips` rebuilds from scratch when needed

---

## Hands-on: Build the reporting model

### Step 4: Create `models/marts/reporting/fct_monthly_zone_revenue.sql`

This is an aggregate table designed for dashboards — monthly revenue broken down by zone and service type:

```sql
select
    coalesce(pickup_zone, 'Unknown Zone') as pickup_zone,
    {% if target.type == 'bigquery' %}cast(date_trunc(pickup_datetime, month) as date)
    {% elif target.type == 'duckdb' %}date_trunc('month', pickup_datetime)
    {% endif %} as revenue_month,
    service_type,

    sum(fare_amount) as revenue_monthly_fare,
    sum(extra) as revenue_monthly_extra,
    sum(mta_tax) as revenue_monthly_mta_tax,
    sum(tip_amount) as revenue_monthly_tip_amount,
    sum(tolls_amount) as revenue_monthly_tolls_amount,
    sum(ehail_fee) as revenue_monthly_ehail_fee,
    sum(improvement_surcharge) as revenue_monthly_improvement_surcharge,
    sum(total_amount) as revenue_monthly_total_amount,

    count(trip_id) as total_monthly_trips,
    avg(passenger_count) as avg_monthly_passenger_count,
    avg(trip_distance) as avg_monthly_trip_distance

from {{ ref('fct_trips') }}
group by pickup_zone, revenue_month, service_type
```

Notice the `{% if target.type %}` block — `DATE_TRUNC` has different syntax in BigQuery vs DuckDB. This pattern makes the model work across both.

---

## Verify it works

At this point, you need seeds loaded and dbt-utils installed. If you've completed Lesson 06 (seeds) and Lesson 10 (packages), run:

```bash
uv run dbt build --select +fct_trips
```

The `+` prefix builds `fct_trips` and ALL its upstream dependencies (staging, intermediate, seeds, dimensions).

For the reporting model:

```bash
uv run dbt run --select fct_monthly_zone_revenue
```

### Check the star schema

```bash
uv run dbt show --inline "select count(*) as trip_count from {{ ref('fct_trips') }}"
uv run dbt show --inline "select count(*) as zone_count from {{ ref('dim_zones') }}"
uv run dbt show --inline "select * from {{ ref('dim_vendors') }}"
```

---

## The complete DAG

Your project now looks like this:

```
source: green_tripdata → stg_green  ─┐
                                      ├→ int_trips_unioned → int_trips → fct_trips → fct_monthly_zone_revenue
source: yellow_tripdata → stg_yellow ─┘          ↑                ↑  ↑
                                     seed: payment_type    dim_zones  dim_vendors
                                                      seed: taxi_zone_lookup
```

---

## What you learned

- Marts contain the final, consumption-ready tables
- Fact tables (`fct_`) hold events/measurements; dimension tables (`dim_`) hold context
- Incremental models only process new rows after the first build
- `{{ this }}` references the model's existing table, `is_incremental()` checks if it exists
- LEFT JOINs to dimension tables enrich facts with human-readable attributes
- Reporting models are pre-aggregated tables optimized for dashboards
- `uv run dbt build --select +model_name` builds a model and all its dependencies

---

**Next: [Lesson 08 — Tests & Data Quality](08_tests_and_data_quality.md)**
