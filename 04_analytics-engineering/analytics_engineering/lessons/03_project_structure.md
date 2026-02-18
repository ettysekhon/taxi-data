# Lesson 03: Project Structure

Every dbt project follows the same layout. This lesson walks through each file and folder so you understand what everything does before you start building models.

---

## The project at a glance

```text
analytics_engineering/
├── dbt_project.yml        ← The most important file
├── packages.yml           ← Third-party packages
├── .gitignore
├── models/                ← Where all your SQL transformations live
│   ├── staging/           ← 1:1 cleaned copies of raw tables
│   ├── intermediate/      ← Complex joins, unions, enrichment
│   └── marts/             ← Final, consumption-ready tables
├── macros/                ← Reusable SQL functions (like Python functions)
├── seeds/                 ← Small CSV files loaded as tables
├── tests/                 ← Custom SQL test assertions
├── snapshots/             ← SCD Type 2 change tracking
└── analyses/              ← Ad-hoc SQL scripts
```

---

## dbt_project.yml — the control center

This is the first file dbt reads when you run any command. If it's missing, nothing works.

Open `dbt_project.yml` and examine it:

```yaml
name: 'analytics_engineering'
version: '1.0.0'

require-dbt-version: [">=1.7.0", "<2.0.0"]

profile: 'analytics_engineering'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

clean-targets:
  - "target"
  - "dbt_packages"

vars:
  dev_start_date: '2019-01-01'
  dev_end_date: '2019-02-01'

models:
  analytics_engineering:
    staging:
      +materialized: view
    intermediate:
      +materialized: table
    marts:
      +materialized: table
```

### Key things to understand

| Field | What it does |
|-------|-------------|
| `name` | Project name. Referenced in the `models:` config section |
| `profile` | Must match the profile name in `~/.dbt/profiles.yml` |
| `*-paths` | Tells dbt where to find each type of file |
| `clean-targets` | Directories deleted by `dbt clean` |
| `vars` | Project-level variables accessible in your SQL via `{{ var('dev_start_date') }}` |
| `models: ... +materialized` | Default materialization per folder |

### Materializations explained

| Type | What it creates | When to use |
|------|----------------|-------------|
| `view` | SQL view (re-runs on every query) | Staging models — light, no storage cost |
| `table` | Physical table (data stored) | Intermediate/mart models — faster queries |
| `incremental` | Table that only processes new rows | Large fact tables — avoids full rebuilds |
| `ephemeral` | CTE (not materialized at all) | Helper logic you don't want as a real table |

---

## The models/ directory

This is where all your transformation SQL lives. dbt recommends three sub-folders:

### staging/

- **1:1 copies** of your raw tables with minimal cleaning
- Rename columns, cast data types, filter obvious garbage
- Prefix files with `stg_`
- Materialized as **views** (lightweight, no data duplication)

### intermediate/

- Everything between raw and ready-to-consume
- Complex joins, unions, deduplication, enrichment
- Prefix files with `int_`
- Materialized as **tables**

### marts/

- Final, consumption-ready tables exposed to business users
- Star schema: fact tables (`fct_`) and dimension tables (`dim_`)
- Only these should be consumed by BI tools
- Materialized as **tables**

> **Convention note**: Some teams use "bronze/silver/gold" (medallion architecture) instead of "staging/intermediate/marts." The concepts are the same.

---

## Other directories

### macros/

Reusable SQL functions written in Jinja. Think of them like Python functions — define once, call anywhere. We'll build several in Lesson 06.

### seeds/

Small CSV files that get loaded into the database via `dbt seed`. Great for lookup tables (zone names, payment type codes) that don't exist in your data warehouse.

### tests/

Custom SQL assertions. If a test query returns any rows, the test fails. Covered in Lesson 08.

### snapshots/

Tracks changes to source tables over time using **SCD Type 2** (Slowly Changing Dimensions). The problem snapshots solve: a source table has a column that overwrites itself (e.g., an order's `status` goes from "pending" to "shipped"), but you need to keep the history of what changed and when.

How it works: each time you run `dbt snapshot`, dbt compares the current data to the previous snapshot. If a value changed, a new row is created with `dbt_valid_from` / `dbt_valid_to` timestamps. The current row always has `dbt_valid_to = NULL`.

This project includes an example snapshot (`snap_zones.sql`) that demonstrates the pattern on zone data. In a real project, you'd snapshot any source where values get overwritten — order statuses, customer addresses, pricing tiers, etc.

Two snapshot strategies:

- **`check`** — compares specific columns; creates a new row if any checked column changed
- **`timestamp`** — uses an `updated_at` column from the source to detect changes

Run snapshots with: `dbt snapshot`

### analyses/

Ad-hoc SQL scripts for investigation. Not materialized — just a scratchpad.

---

## Hands-on: Explore the project

### Exercise 1: Run dbt debug

```bash
cd analytics_engineering
uv run dbt debug
```

Confirm all checks pass. This verifies `dbt_project.yml` and `profiles.yml` are correctly linked.

### Exercise 2: Run dbt compile

```bash
uv run dbt compile
```

This compiles all your models (resolves Jinja, `ref()`, `source()`) without executing anything. After running, look inside `target/compiled/` — you'll see the pure SQL that dbt would send to the database.

Right now there's not much to compile, but this is a command you'll use constantly during development.

### Exercise 3: Examine the project variables

Open `dbt_project.yml` and find the `vars:` section. These variables (`dev_start_date`, `dev_end_date`) will be used in staging models to limit data in the dev environment. You access them in SQL with `{{ var('dev_start_date') }}`.

---

## What you learned

- Every dbt project starts with `dbt_project.yml`
- Models live in three layers: staging → intermediate → marts
- Materializations control how dbt creates the output (view, table, incremental)
- `dbt compile` is your fast feedback loop — no warehouse cost, catches Jinja errors early
- The project structure mirrors Kimball's kitchen analogy: pantry → kitchen → dining hall

---

**Next: [Lesson 04 — Sources & Staging Models](04_sources_and_staging_models.md)**
