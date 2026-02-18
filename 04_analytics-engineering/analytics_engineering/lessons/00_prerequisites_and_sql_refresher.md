# Lesson 00: Prerequisites & SQL Refresher

Before diving into dbt, make sure you're comfortable with a few SQL concepts that show up constantly in analytics engineering. This lesson is a refresher — if you already know CTEs and window functions well, skim through and move on.

---

## Why this matters for dbt

Every dbt model is a SELECT statement. That's literally it — you write SQL, and dbt handles the rest (creating tables, managing dependencies, running tests). So strong SQL is the foundation of everything we'll do.

Two patterns come up repeatedly:

- **CTEs** — dbt models are structured as chains of CTEs. It's the standard way to write readable, modular SQL in dbt.
- **Window functions** — used for deduplication, ranking, running totals, and enrichment. We'll use `ROW_NUMBER()` to deduplicate our trip data later in the project.

---

## Common Table Expressions (CTEs)

A CTE is a temporary named result set that exists only for the duration of a query. Think of it as giving a name to a subquery so you can reference it later.

```sql
WITH cte_name AS (
    SELECT column1, column2
    FROM some_table
    WHERE condition
)
SELECT * FROM cte_name;
```

### Why CTEs matter in dbt

dbt models are built as chains of CTEs. This is the standard pattern you'll see in every well-written dbt project:

```sql
with source as (
    select * from {{ source('raw', 'green_tripdata') }}
),

renamed as (
    select
        cast(vendorid as integer) as vendor_id,
        cast(lpep_pickup_datetime as timestamp) as pickup_datetime
    from source
)

select * from renamed
```

Each CTE does one thing. The final `select` pulls from the last CTE. This makes the logic easy to follow and debug.

### Example: finding the second-largest trip

```sql
WITH ranked_trips AS (
    SELECT
        lpep_pickup_datetime,
        total_amount,
        RANK() OVER (ORDER BY total_amount DESC) AS rank
    FROM greentaxi_trips
)

SELECT * FROM ranked_trips WHERE rank = 2;
```

---

## Window Functions

A window function performs a calculation across a set of rows related to the current row — without collapsing those rows into a single output (unlike GROUP BY).

```sql
FUNCTION() OVER (PARTITION BY column ORDER BY column)
```

The `OVER()` clause defines the "window" — which rows to include in the calculation.

- **PARTITION BY** — divides rows into groups (optional)
- **ORDER BY** — defines the order within each group

### ROW_NUMBER()

Assigns a sequential number to each row within a partition. This is the most important window function for analytics engineering because it's how you **deduplicate data**.

```sql
SELECT
    total_amount,
    PULocationID,
    ROW_NUMBER() OVER (
        PARTITION BY PULocationID
        ORDER BY total_amount DESC
    ) AS ranking
FROM greentaxi_trips;
```

This numbers rows 1, 2, 3... within each pickup location, ordered by fare amount. To keep only the top row per group, you'd filter `WHERE ranking = 1`.

**We'll use exactly this pattern** in Lesson 05 to deduplicate taxi trips.

### RANK() and DENSE_RANK()

Similar to ROW_NUMBER(), but they handle ties differently:

| Score | ROW_NUMBER() | RANK() | DENSE_RANK() |
|-------|-------------|--------|--------------|
| 95    | 1           | 1      | 1            |
| 90    | 2           | 2      | 2            |
| 90    | 3           | 2      | 2            |
| 85    | 4           | 4      | 3            |

- **ROW_NUMBER()** — always unique, even for ties
- **RANK()** — same rank for ties, skips numbers after
- **DENSE_RANK()** — same rank for ties, no gaps

### LAG() and LEAD()

Pull values from adjacent rows without a self-join:

```sql
SELECT
    lpep_pickup_datetime,
    total_amount,
    LAG(total_amount) OVER (ORDER BY lpep_pickup_datetime) AS prev_total,
    LEAD(total_amount) OVER (ORDER BY lpep_pickup_datetime) AS next_total
FROM greentaxi_trips
ORDER BY lpep_pickup_datetime;
```

Useful for calculating period-over-period changes, time between events, etc.

### PERCENTILE_CONT()

Computes percentiles across a partition:

```sql
SELECT
    PULocationID,
    total_amount,
    PERCENTILE_CONT(total_amount, 0.9) OVER (PARTITION BY PULocationID) AS p90
FROM greentaxi_trips;
```

The p90 value means 90% of trips from that location have a total amount at or below this number.

---

## The QUALIFY clause (DuckDB feature)

DuckDB supports `QUALIFY`, which filters on window function results directly — no subquery or CTE needed:

```sql
SELECT *
FROM trips
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY vendor_id, pickup_datetime
    ORDER BY dropoff_datetime
) = 1
```

This is equivalent to wrapping in a CTE and filtering `WHERE row_num = 1`, but more concise. We'll use this in our intermediate model for deduplication.

---

## Self-check

Before moving on, make sure you can answer these:

1. What's the difference between a CTE and a subquery?
2. When would you use ROW_NUMBER() vs RANK()?
3. How would you keep only the first row per group using a window function?
4. What does QUALIFY do that a WHERE clause can't?

---

**Next: [Lesson 01 — Analytics Engineering & dbt](01_analytics_engineering_and_dbt.md)**
