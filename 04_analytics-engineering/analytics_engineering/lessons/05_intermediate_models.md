# Lesson 05: Intermediate Models

Your staging models are clean and typed. Now you need to combine yellow and green taxi data into a single dataset, enrich it, and deduplicate it. That's what the intermediate layer is for.

---

## ref() vs source() — the key distinction

Up until now, every model has pulled from raw data using `{{ source() }}`. From here on, your inputs are **other dbt models**, so you use `{{ ref() }}` instead.

| Function | When to use | Example |
|----------|------------|---------|
| `{{ source('raw', 'green_tripdata') }}` | Pulling from raw tables declared in sources.yml | Staging models |
| `{{ ref('stg_green_tripdata') }}` | Pulling from another dbt model | Everything after staging |

Why does this matter? `ref()` automatically builds the **dependency graph**. dbt knows that if model B refs model A, then A must run first. You never manage run order yourself.

---

## The union problem

We have two staging models (`stg_green_tripdata` and `stg_yellow_tripdata`) and we want to combine them. But they're not identical — green has two columns that yellow doesn't:

### `trip_type`

- `1` = street hail (flag down the taxi)
- `2` = booked via phone or app
- Yellow taxis can **only** be hailed on the street (by law), so they don't have this column
- **Fix**: hard-code `trip_type = 1` for yellow

### `ehail_fee`

- An extra fee for app-requested rides
- Yellow taxis never have this fee
- **Fix**: hard-code `ehail_fee = 0` for yellow

This isn't just a technical issue — it's a **business story**. Yellow cabs operate in Manhattan, green cabs were created for the outer boroughs. Understanding the domain helps you make the right decisions about how to handle schema mismatches.

---

## Hands-on: Build the intermediate models

### Step 1: Create `models/intermediate/int_trips_unioned.sql`

This model unions green and yellow data with aligned schemas:

```sql
with green_trips as (
    select
        vendor_id,
        rate_code_id,
        pickup_location_id,
        dropoff_location_id,
        pickup_datetime,
        dropoff_datetime,
        store_and_fwd_flag,
        passenger_count,
        trip_distance,
        trip_type,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        ehail_fee,
        improvement_surcharge,
        total_amount,
        payment_type,
        'Green' as service_type
    from {{ ref('stg_green_tripdata') }}
),

yellow_trips as (
    select
        vendor_id,
        rate_code_id,
        pickup_location_id,
        dropoff_location_id,
        pickup_datetime,
        dropoff_datetime,
        store_and_fwd_flag,
        passenger_count,
        trip_distance,
        cast(1 as integer) as trip_type,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        cast(0 as numeric) as ehail_fee,
        improvement_surcharge,
        total_amount,
        payment_type,
        'Yellow' as service_type
    from {{ ref('stg_yellow_tripdata') }}
)

select * from green_trips
union all
select * from yellow_trips
```

### What's happening

1. **Explicit column lists** — instead of `SELECT *`, we list every column. This ensures both sides of the UNION have the same schema.
2. **Schema alignment** — yellow gets `trip_type = 1` and `ehail_fee = 0` to match green's schema.
3. **Service type tag** — a new column `service_type` ('Green' or 'Yellow') so we can always tell which dataset a row came from.
4. **UNION ALL** — not UNION. UNION removes duplicates (expensive), UNION ALL keeps everything (we'll handle duplicates explicitly in the next model).

### Step 2: Create `models/intermediate/int_trips.sql`

This model enriches and deduplicates the unioned data:

```sql
with unioned as (
    select * from {{ ref('int_trips_unioned') }}
),

payment_types as (
    select * from {{ ref('payment_type_lookup') }}
),

cleaned_and_enriched as (
    select
        {{ dbt_utils.generate_surrogate_key(['u.vendor_id', 'u.pickup_datetime', 'u.pickup_location_id', 'u.service_type']) }} as trip_id,

        u.vendor_id,
        u.service_type,
        u.rate_code_id,
        u.pickup_location_id,
        u.dropoff_location_id,
        u.pickup_datetime,
        u.dropoff_datetime,
        u.store_and_fwd_flag,
        u.passenger_count,
        u.trip_distance,
        u.trip_type,
        u.fare_amount,
        u.extra,
        u.mta_tax,
        u.tip_amount,
        u.tolls_amount,
        u.ehail_fee,
        u.improvement_surcharge,
        u.total_amount,
        coalesce(u.payment_type, 0) as payment_type,
        coalesce(pt.description, 'Unknown') as payment_type_description

    from unioned u
    left join payment_types pt
        on coalesce(u.payment_type, 0) = pt.payment_type
)

select * from cleaned_and_enriched

qualify row_number() over(
    partition by vendor_id, pickup_datetime, pickup_location_id, service_type
    order by dropoff_datetime
) = 1
```

### What's happening

1. **Surrogate key** — `{{ dbt_utils.generate_surrogate_key([...]) }}` creates a unique `trip_id` by hashing multiple columns. This comes from the dbt-utils package (we'll install it in Lesson 10, but reference it now).
2. **Payment enrichment** — LEFT JOIN to the `payment_type_lookup` seed (we'll create this in Lesson 06) to get human-readable payment descriptions.
3. **COALESCE for nulls** — null payment types become 0, which maps to "Unknown."
4. **Deduplication with QUALIFY** — if multiple trips match on (vendor, timestamp, location, service_type), keep only the first by dropoff time. This uses the `QUALIFY` + `ROW_NUMBER()` pattern from Lesson 00.

> **Note**: This model references `payment_type_lookup` (a seed) and `dbt_utils` (a package). We'll create those in Lessons 06 and 10 respectively. For now, understand the *pattern* — we'll make it runnable soon.

---

## The dependency graph

After building these models, dbt's DAG looks like this:

```
source: raw.green_tripdata  →  stg_green_tripdata  ─┐
                                                      ├→  int_trips_unioned  →  int_trips
source: raw.yellow_tripdata →  stg_yellow_tripdata  ─┘                           ↑
                                                                    seed: payment_type_lookup
```

dbt builds this graph automatically from your `ref()` and `source()` calls. You never tell it the order — it figures it out.

---

## Verify it works

You can't run `int_trips` yet (it needs the seed and package). But you can run the union model:

```bash
uv run dbt run --select int_trips_unioned
```

If you want to run everything from staging through the union:

```bash
uv run dbt run --select +int_trips_unioned
```

The `+` prefix means "this model AND all its upstream dependencies."

### Preview the data

```bash
uv run dbt show --select int_trips_unioned --limit 5
```

You should see rows from both green and yellow trips, with the `service_type` column distinguishing them.

---

## dbt-utils alternatives: union_relations and deduplicate

We wrote the union and deduplication by hand above. dbt-utils provides macros for both of these, and you'll encounter them in real projects:

### union_relations

Instead of manually writing two CTEs and UNION ALL:

```sql
{{ dbt_utils.union_relations(
    relations=[ref('stg_green_tripdata'), ref('stg_yellow_tripdata')],
    source_column_name='_source_relation'
) }}
```

This auto-unions the two models, handles different column orders, and adds a `_source_relation` column to track origin. **Missing columns are filled with NULL.**

We didn't use it here because we needed *specific default values* for the missing columns (`trip_type = 1` for yellow, `ehail_fee = 0` for yellow). `union_relations` can't inject business-logic defaults — it only fills NULLs. When your schemas are identical or NULLs are acceptable, `union_relations` is cleaner.

### deduplicate

Instead of `QUALIFY row_number() OVER(...) = 1`:

```sql
{{ dbt_utils.deduplicate(
    relation='my_cte',
    partition_by='vendor_id, pickup_datetime, pickup_location_id, service_type',
    order_by='dropoff_datetime desc',
) }}
```

This generates the same `ROW_NUMBER()` pattern under the hood. We used `QUALIFY` directly because it reads more naturally when combined with inline enrichment (the surrogate key and payment join happen in the same CTE). In simpler cases, `deduplicate` saves boilerplate.

**Rule of thumb**: Use the manual approach when you need business logic interleaved with the operation. Use the dbt-utils macro when it's a straightforward dedup or union.

---

## What you learned

- `ref()` is for dbt models, `source()` is for raw tables
- `ref()` automatically builds the dependency graph
- When unioning datasets with different schemas, align them by adding missing columns with default values
- `UNION ALL` keeps all rows; handle duplicates explicitly
- Surrogate keys provide unique identifiers when the source doesn't have one
- `QUALIFY` + `ROW_NUMBER()` is the cleanest deduplication pattern in DuckDB
- The `+` prefix in `--select` pulls in upstream dependencies
- dbt-utils provides `union_relations` and `deduplicate` for common patterns

---

**Next: [Lesson 06 — Seeds & Macros](06_seeds_and_macros.md)**
