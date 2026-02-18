# Lesson 10: Packages

dbt packages are like Python libraries — self-contained dbt projects with macros, tests, and models that you can drop into your own project. This lesson covers how to install and use them, with a deep dive into dbt-utils.

---

## Hands-on: Install packages

### Step 1: Verify `packages.yml`

At the project root, you should have:

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.3.0", "<2.0.0"]
  - package: dbt-labs/codegen
    version: [">=0.14.0", "<1.0.0"]
```

### Step 2: Install

```bash
uv run dbt deps
```

This creates:

- `dbt_packages/` — the installed source code (git-ignored)
- `package-lock.yml` — pinned versions for reproducibility (commit this)

---

## dbt-utils: the full inventory

dbt-utils (maintained by dbt Labs) is the essential package. Here's every macro it provides, grouped by what you'd use them for.

### SQL generators — data transformation macros

These generate SQL at compile time, cross-database compatible.

| Macro | What it does | Used in this project? |
|-------|-------------|----------------------|
| `generate_surrogate_key` | Hashes columns into a unique ID | **Yes** — `int_trips.sql` |
| `deduplicate` | Removes duplicate rows (ROW_NUMBER pattern) | No (we use QUALIFY directly) |
| `union_relations` | Unions multiple models, handling schema differences | No (we need custom defaults) |
| `star` | Selects all columns from a relation, with exclusions | No |
| `safe_divide` | Division returning NULL when denominator is 0 | No |
| `safe_add` / `safe_subtract` | Addition/subtraction handling NULLs | No |
| `pivot` / `unpivot` | Pivot rows to columns and vice versa | No |
| `date_spine` | Generates a series of dates (useful for filling gaps) | No |
| `haversine_distance` | Calculates distance between two lat/lon points | No |
| `generate_series` | Generates a series of integers | No |
| `group_by` | Generates `GROUP BY 1, 2, 3...` for N columns | No |
| `width_bucket` | Assigns values to equally-spaced buckets | No |

### Generic tests — data quality assertions

Apply these in your `schema.yml` just like the built-in tests.

| Test | What it checks |
|------|---------------|
| `unique_combination_of_columns` | No duplicate rows for a set of columns (used in `fct_monthly_zone_revenue`) |
| `accepted_range` | Values fall within a min/max range |
| `expression_is_true` | An arbitrary SQL expression evaluates to true for all rows |
| `not_null_proportion` | At least X% of values are not null |
| `at_least_one` | Column has at least one non-null value |
| `not_constant` | Column has more than one distinct value |
| `not_empty_string` | Column has no empty strings |
| `not_accepted_values` | Inverse of accepted_values — these values must NOT appear |
| `relationships_where` | Referential integrity with a WHERE filter |
| `recency` | Most recent value is within a time window |
| `equal_rowcount` | Two models have the same number of rows |
| `fewer_rows_than` | Model A has fewer rows than model B |
| `equality` | Two models produce identical results |
| `cardinality_equality` | Two columns have the same number of distinct values |
| `mutually_exclusive_ranges` | Date/number ranges don't overlap |
| `sequential_values` | Values increment by a fixed amount (no gaps) |

### Introspective macros — query your database metadata

| Macro | What it does |
|-------|-------------|
| `get_column_values` | Returns distinct values of a column as a list |
| `get_filtered_columns_in_relation` | Lists column names matching a filter |
| `get_relations_by_pattern` / `get_relations_by_prefix` | Finds tables matching a naming pattern |
| `get_query_results_as_dict` | Runs a query and returns results as a Jinja dict |
| `get_single_value` | Returns a single scalar value from a query |

### Web macros

| Macro | What it does |
|-------|-------------|
| `get_url_parameter` | Extracts a parameter from a URL string |
| `get_url_host` | Extracts the host from a URL |
| `get_url_path` | Extracts the path from a URL |

---

## Macros we use in this project

### generate_surrogate_key

Creates a unique trip ID by hashing multiple columns:

```sql
{{ dbt_utils.generate_surrogate_key(
    ['vendor_id', 'pickup_datetime', 'pickup_location_id', 'service_type']
) }} as trip_id
```

The hash function is warehouse-specific (MD5 on BigQuery, etc.) — dbt-utils handles the difference.

### unique_combination_of_columns

Tests that no two rows share the same combination of columns:

```yaml
data_tests:
  - dbt_utils.unique_combination_of_columns:
      arguments:
        combination_of_columns:
          - pickup_zone
          - revenue_month
          - service_type
```

More flexible than `unique` on a single column.

---

## Macros worth knowing for real projects

### safe_divide — prevent divide-by-zero

```sql
{{ dbt_utils.safe_divide('revenue', 'trips') }} as revenue_per_trip
```

Returns NULL instead of erroring when `trips` is 0.

### star — select all except specific columns

```sql
select
    {{ dbt_utils.star(from=ref('stg_green_tripdata'), except=['ehail_fee']) }}
from {{ ref('stg_green_tripdata') }}
```

Useful when you want most columns but need to exclude a few.

### date_spine — fill date gaps

```sql
{{ dbt_utils.date_spine(
    datepart="day",
    start_date="cast('2019-01-01' as date)",
    end_date="cast('2020-12-31' as date)"
) }}
```

Generates one row per day. Essential for time-series analysis where you need rows even for days with no data.

### expression_is_true — flexible test assertions

```yaml
data_tests:
  - dbt_utils.expression_is_true:
      arguments:
        expression: "total_amount >= fare_amount"
```

Tests any arbitrary SQL condition across all rows.

### accepted_range — value bounds

```yaml
columns:
  - name: passenger_count
    data_tests:
      - dbt_utils.accepted_range:
          arguments:
            min_value: 0
            max_value: 10
```

---

## Other packages worth knowing

### dbt-codegen

Auto-generates YAML and SQL scaffolding:

```bash
uv run dbt run-operation generate_model_yaml --args '{"model_names": ["stg_green_tripdata"]}'
uv run dbt run-operation generate_base_model --args '{"source_name": "raw", "table_name": "green_tripdata"}'
```

### dbt-expectations

A massive library of pre-built tests. Before writing a custom test, check if dbt-expectations already has it.

### dbt-audit-helper

Compares two models for equality. Essential when refactoring — verifies your rewrite produces the same results.

### dbt-project-evaluator

Scores your project against best practices.

---

## A note on trust

Packages on [hub.getdbt.com](https://hub.getdbt.com) are vetted by dbt Labs. Packages from random GitHub repos should be reviewed before use.

---

## Verify it works

With packages installed, build the full project:

```bash
uv run dbt build --target prod
```

---

## What you learned

- dbt packages are installed via `packages.yml` and `dbt deps`
- dbt-utils is the essential package: surrogate keys, dedup, union, safe math, date spines, and 16+ generic tests
- `generate_surrogate_key` and `unique_combination_of_columns` are the two most commonly used macros
- `deduplicate` and `union_relations` automate common patterns (but manual SQL is better when business logic is interleaved)
- `package-lock.yml` pins versions for reproducibility — commit it
- `dbt_packages/` is git-ignored — it's rebuilt by `dbt deps`

---

**Next: [Lesson 11 — Commands Reference](11_commands_reference.md)**
