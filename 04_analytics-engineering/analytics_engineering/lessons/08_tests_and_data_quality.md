# Lesson 08: Tests & Data Quality

Wrong numbers in dashboards have exactly two causes: the data wasn't what you expected, or you messed up the SQL. Tests help you catch both before stakeholders do.

---

## Types of tests in dbt

dbt offers several testing mechanisms:

| Type | Where it lives | How it works |
|------|---------------|-------------|
| **Generic tests** | YAML (schema.yml) | Built-in and custom parameterized tests |
| **Singular tests** | `tests/*.sql` | Custom SQL — if it returns rows, it fails |
| **Source freshness** | `sources.yml` | Checks if data is stale |
| **Unit tests** | YAML (models/) | Test SQL logic with mock data (dbt 1.8+) |
| **Model contracts** | YAML (schema.yml) | Prevent building if schema doesn't match |

---

## 1. Generic tests — the workhorses

These are the most common. dbt ships with four built-in generic tests:

| Test | What it checks |
|------|---------------|
| `unique` | No duplicate values in a column |
| `not_null` | No null values |
| `accepted_values` | Values must be in a defined list |
| `relationships` | Every value must exist in another table (referential integrity) |

You declare them in your `schema.yml` alongside column descriptions.

---

## Hands-on: Add tests to your models

### Step 1: Create `models/staging/schema.yml`

```yaml
models:
  - name: stg_green_tripdata
    description: >
      Staging model for green taxi trip data. Standardizes column names
      and data types from the raw green_tripdata source.
    columns:
      - name: vendor_id
        description: Taxi technology provider
        data_tests:
          - not_null
      - name: pickup_datetime
        description: Date and time when the meter was engaged
        data_tests:
          - not_null

  - name: stg_yellow_tripdata
    description: >
      Staging model for yellow taxi trip data. Standardizes column names
      and data types from the raw yellow_tripdata source.
    columns:
      - name: vendor_id
        description: Taxi technology provider
        data_tests:
          - not_null
      - name: pickup_datetime
        description: Date and time when the meter was engaged
        data_tests:
          - not_null
```

### Step 2: Create `models/intermediate/schema.yml`

```yaml
models:
  - name: int_trips_unioned
    description: Union of green and yellow taxi trip data with normalized schema
    columns:
      - name: vendor_id
        description: Taxi technology provider ID
      - name: service_type
        description: Type of taxi service (Green or Yellow)

  - name: int_trips
    description: Cleaned, enriched, and deduplicated trip data ready for marts
    columns:
      - name: trip_id
        description: Unique trip identifier (surrogate key)
        data_tests:
          - unique
          - not_null
      - name: vendor_id
        description: Taxi technology provider ID
        data_tests:
          - not_null
      - name: service_type
        description: Type of taxi service (Green or Yellow)
        data_tests:
          - not_null
          - accepted_values:
              arguments:
                values: ['Green', 'Yellow']
      - name: pickup_datetime
        description: Timestamp when meter was engaged
        data_tests:
          - not_null
      - name: total_amount
        description: Total amount charged to passenger
        data_tests:
          - not_null
```

### Step 3: Create `models/marts/schema.yml`

This is the most thorough — mart tables are what end users see, so they deserve the most testing:

```yaml
models:
  - name: dim_zones
    description: Taxi zone dimension table with location details
    columns:
      - name: location_id
        description: Unique identifier for each taxi zone
        data_tests:
          - unique
          - not_null
      - name: borough
        description: NYC borough name
      - name: zone
        description: Specific zone name within the borough
      - name: service_zone
        description: Service zone classification

  - name: dim_vendors
    description: Taxi technology vendor dimension table
    columns:
      - name: vendor_id
        description: Unique vendor identifier
        data_tests:
          - unique
          - not_null
      - name: vendor_name
        description: Company name of the vendor

  - name: fct_trips
    description: Fact table with all taxi trips including trip and payment details
    config:
      contract:
        enforced: true
    columns:
      - name: trip_id
        description: Unique trip identifier
        data_type: string
        data_tests:
          - unique
          - not_null
      - name: vendor_id
        description: Taxi technology provider
        data_type: integer
        data_tests:
          - not_null
      - name: service_type
        description: Type of taxi service (Green or Yellow)
        data_type: string
        data_tests:
          - accepted_values:
              arguments:
                values: ['Green', 'Yellow']
          - not_null
      - name: rate_code_id
        data_type: integer
      - name: pickup_location_id
        description: TLC Taxi Zone where trip started
        data_type: integer
        data_tests:
          - relationships:
              arguments:
                to: ref('dim_zones')
                field: location_id
      - name: pickup_borough
        data_type: string
      - name: pickup_zone
        data_type: string
      - name: dropoff_location_id
        description: TLC Taxi Zone where trip ended
        data_type: integer
        data_tests:
          - relationships:
              arguments:
                to: ref('dim_zones')
                field: location_id
      - name: dropoff_borough
        data_type: string
      - name: dropoff_zone
        data_type: string
      - name: pickup_datetime
        description: Timestamp when meter was engaged
        data_type: timestamp
        data_tests:
          - not_null
      - name: dropoff_datetime
        data_type: timestamp
      - name: store_and_fwd_flag
        data_type: string
      - name: passenger_count
        data_type: integer
      - name: trip_distance
        data_type: numeric
      - name: trip_type
        data_type: integer
      - name: trip_duration_minutes
        data_type: bigint
      - name: fare_amount
        data_type: numeric
      - name: extra
        data_type: numeric
      - name: mta_tax
        data_type: numeric
      - name: tip_amount
        data_type: numeric
      - name: tolls_amount
        data_type: numeric
      - name: ehail_fee
        data_type: numeric
      - name: improvement_surcharge
        data_type: numeric
      - name: total_amount
        description: Total amount charged
        data_type: numeric
        data_tests:
          - not_null
      - name: payment_type
        data_type: integer
      - name: payment_type_description
        data_type: string
```

### Step 4: Create `models/marts/reporting/schema.yml`

```yaml
models:
  - name: fct_monthly_zone_revenue
    description: Monthly revenue aggregation by pickup zone and service type
    data_tests:
      - dbt_utils.unique_combination_of_columns:
          arguments:
            combination_of_columns:
              - pickup_zone
              - revenue_month
              - service_type
    columns:
      - name: pickup_zone
        description: Pickup zone where revenue was generated
        data_tests:
          - not_null
      - name: revenue_month
        description: Month for revenue aggregation
        data_tests:
          - not_null
      - name: service_type
        description: Service type (Green or Yellow)
        data_tests:
          - not_null
          - accepted_values:
              arguments:
                values: ['Green', 'Yellow']
      - name: revenue_monthly_total_amount
        description: Monthly sum of total fares
        data_tests:
          - not_null
      - name: total_monthly_trips
        description: Count of trips in the month
        data_tests:
          - not_null
```

---

## 2. Source freshness tests

These are already in your `sources.yml` from Lesson 04:

```yaml
freshness:
  warn_after: {count: 24, period: hour}
  error_after: {count: 48, period: hour}
```

Run them with:

```bash
uv run dbt source freshness
```

This checks when data was last loaded. Since our data is from 2019-2020, these will always show as stale — but in a production pipeline, this catches real problems.

---

## 3. Model contracts

Notice the `config: contract: enforced: true` on `fct_trips`. This means dbt will **refuse to build** the model if its output doesn't match the defined columns and data types. It's a guarantee to downstream consumers that the table shape won't change unexpectedly.

Contracts are especially useful when:

- Multiple teams consume your data
- You have SLAs on table structure
- You want to catch breaking changes in CI/CD

---

## 4. Singular tests (optional exercise)

Create a custom test in `tests/`:

```sql
-- tests/assert_positive_total_amount.sql
select
    trip_id,
    total_amount
from {{ ref('fct_trips') }}
where total_amount < 0
```

If any trips have negative totals, this test fails. Singular tests are great for business rules that don't fit the generic test patterns.

---

## Verify it works

### Run all tests

```bash
uv run dbt test
```

Or run tests for a specific model:

```bash
uv run dbt test --select fct_trips
```

### Run build (models + tests together)

```bash
uv run dbt build --select +fct_trips
```

`uv run dbt build` is smarter than running `uv run dbt run` then `uv run dbt test` separately — it's DAG-aware. If a model fails its tests, dbt skips all downstream models.

---

## What you learned

- Generic tests (`unique`, `not_null`, `accepted_values`, `relationships`) are declared in YAML
- Singular tests are SQL files in `tests/` — if they return rows, they fail
- Source freshness checks catch stale data
- Model contracts prevent schema drift by failing the build if output doesn't match
- `uv run dbt test` runs all tests; `uv run dbt build` runs models AND tests in dependency order
- Test heavily on marts (what users see) and key columns on intermediate models

---

**Next: [Lesson 09 — Documentation](09_documentation.md)**
