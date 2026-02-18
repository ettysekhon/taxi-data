# Lesson 06: Seeds & Macros

Our intermediate model needs lookup data (payment types, taxi zones) and reusable SQL logic. This lesson covers the two dbt features that handle those needs: **seeds** for loading small CSV files, and **macros** for writing reusable SQL functions.

---

## Seeds — bringing in lookup data

### What are seeds?

Seeds are CSV files in your `seeds/` directory that dbt loads directly into the database. You run `dbt seed` and they become queryable tables, referenced with `{{ ref('filename') }}` just like any model.

### When to use seeds

- Lookup tables that don't exist in your warehouse
- Small, static reference data (< a few thousand rows)
- Quick experiments before committing to a proper data load

### When NOT to use seeds

- Large datasets (CSVs in git slow down pulls/pushes)
- Confidential data (seeds are committed to your repo)
- Data that changes frequently (use a proper source instead)

---

## Hands-on: Create seed files

### Step 1: Create `seeds/payment_type_lookup.csv`

```csv
payment_type,description
0,Unknown
1,Credit card
2,Cash
3,No charge
4,Dispute
5,Unknown
6,Voided trip
```

### Step 2: Create `seeds/taxi_zone_lookup.csv`

This file has 265 rows mapping location IDs to borough and zone names. Copy it from the existing project or download it from the [NYC TLC data dictionary](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf).

The first few rows look like:

```csv
"locationid","borough","zone","service_zone"
1,"EWR","Newark Airport","EWR"
2,"Queens","Jamaica Bay","Boro Zone"
3,"Bronx","Allerton/Pelham Gardens","Boro Zone"
4,"Manhattan","Alphabet City","Yellow Zone"
```

### Step 3: Create `seeds/seeds_properties.yml`

Document your seeds so people know what they are:

```yaml
seeds:
  - name: taxi_zone_lookup
    description: >
      Taxi Zones based on NYC Department of City Planning's Neighborhood
      Tabulation Areas (NTAs). Maps location IDs to boroughs and zone names.

  - name: payment_type_lookup
    description: >
      Payment type reference data mapping numeric codes to descriptions.
    columns:
      - name: payment_type
        description: Numeric code for payment type
        data_tests:
          - unique
          - not_null
      - name: description
        description: Human-readable description of payment method
```

### Step 4: Load the seeds

```bash
uv run dbt seed
```

You should see both seeds loaded. They're now available as `{{ ref('payment_type_lookup') }}` and `{{ ref('taxi_zone_lookup') }}` in any model.

---

## Macros — reusable SQL functions

### The problem

Right now, if you want to map vendor IDs to company names, you'd write a CASE statement:

```sql
case vendor_id
    when 1 then 'Creative Mobile Technologies'
    when 2 then 'VeriFone Inc.'
end
```

This works, but what if you need the same mapping in multiple models? You'd copy-paste it everywhere. When a new vendor appears, you'd have to find and update every copy. That's fragile.

### The solution: macros

Macros are Jinja functions defined in `.sql` files inside `macros/`. You write the logic once and call it anywhere.

---

## Hands-on: Create macros

### Step 5: Create `macros/get_vendor_data.sql`

```sql
{% macro get_vendor_data(vendor_id_column) %}

{% set vendors = {
    1: 'Creative Mobile Technologies',
    2: 'VeriFone Inc.',
    4: 'Unknown/Other'
} %}

case {{ vendor_id_column }}
    {% for vendor_id, vendor_name in vendors.items() %}
    when {{ vendor_id }} then '{{ vendor_name }}'
    {% endfor %}
end

{% endmacro %}
```

### How this works

1. `{% macro get_vendor_data(vendor_id_column) %}` — defines a macro that takes one argument
2. `{% set vendors = {...} %}` — creates a Jinja dictionary (like a Python dict)
3. The `{% for %}` loop generates CASE WHEN clauses at **compile time**
4. When you call `{{ get_vendor_data('vendor_id') }}` in a model, dbt replaces it with the generated SQL

### What the compiled SQL looks like

When dbt compiles `{{ get_vendor_data('vendor_id') }}`, it produces:

```sql
case vendor_id
    when 1 then 'Creative Mobile Technologies'
    when 2 then 'VeriFone Inc.'
    when 4 then 'Unknown/Other'
end
```

The Jinja is gone — it's just plain SQL by the time it hits the database.

### Step 6: Create `macros/get_trip_duration_minutes.sql`

```sql
{% macro get_trip_duration_minutes(pickup_datetime, dropoff_datetime) %}
    {{ dbt.datediff(pickup_datetime, dropoff_datetime, 'minute') }}
{% endmacro %}
```

This uses dbt's built-in `datediff` macro, which is **cross-database compatible** — it generates the right SQL whether you're on DuckDB, BigQuery, Snowflake, or PostgreSQL.

### Step 7: Create `macros/safe_cast.sql`

```sql
{% macro safe_cast(column, data_type) %}
    {% if target.type == 'bigquery' %}
        safe_cast({{ column }} as {{ data_type }})
    {% else %}
        cast({{ column }} as {{ data_type }})
    {% endif %}
{% endmacro %}
```

BigQuery has `SAFE_CAST` (returns NULL instead of erroring on bad data). Other databases don't. This macro handles the difference automatically.

### Step 8: Create `macros/macros_properties.yml`

```yaml
macros:
  - name: get_trip_duration_minutes
    description: >
      Calculates trip duration in minutes using dbt's cross-database datediff.
    arguments:
      - name: pickup_datetime
        type: timestamp
        description: The pickup timestamp
      - name: dropoff_datetime
        type: timestamp
        description: The dropoff timestamp

  - name: get_vendor_data
    description: >
      Generates a CASE statement mapping vendor_id to vendor_name.
      Uses a Jinja dictionary for maintainability.
    arguments:
      - name: vendor_id_column
        type: integer
        description: The column name containing the vendor ID
```

---

## Verify it works

### Check seeds are loaded

```bash
uv run dbt show --inline "select * from {{ ref('payment_type_lookup') }}"
```

You should see the 7 payment types.

### Check macros compile

```bash
uv run dbt compile --select int_trips
```

Look at `target/compiled/.../int_trips.sql` and you'll see the surrogate key macro expanded into actual SQL. (Note: `int_trips` won't fully compile until you install dbt-utils in Lesson 10.)

---

## What you learned

- Seeds load CSV files into the database with `dbt seed` and are referenced with `ref()`
- Macros are reusable Jinja functions defined in `macros/*.sql`
- Macros are resolved at **compile time** — by the time SQL hits the database, all Jinja is gone
- `{% set %}` creates variables, `{% for %}` loops, `{% if %}` branches — all standard Jinja
- dbt's built-in macros (like `dbt.datediff`) provide cross-database compatibility
- Document macros and seeds in YAML just like models

---

**Next: [Lesson 07 — Marts: Fact & Dimension Tables](07_marts_fact_and_dimension_tables.md)**
