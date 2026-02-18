# Analytics Engineering with dbt Core & DuckDB

A practical, ground-up tutorial for learning analytics engineering by building a real dbt project on NYC taxi trip data based on the [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) Module 4 by DataTalksClub.

## What you'll build

By the end of this tutorial, you will have built a complete dbt project that transforms raw NYC taxi trip data into a production-ready star schema:

```text
Raw Data (Parquet files)
    ↓
Sources (DuckDB tables)
    ↓
Staging Models (cleaned, typed, renamed)
    ↓
Intermediate Models (unioned, enriched, deduplicated)
    ↓
Mart Models (star schema: fact + dimension tables)
    ↓
Reporting Models (aggregated for dashboards)
```

## Prerequisites

- Python 3.9+
- Basic SQL knowledge (CTEs, JOINs, GROUP BY)
- A terminal / command line
- VS Code (recommended) or any text editor

## Curriculum

Work through the lessons in order. Each lesson teaches one concept, explains why it matters, walks you through a hands-on exercise, and ends with a verification step.

| # | Lesson | What you'll learn | Hands-on? |
|---|--------|-------------------|-----------|
| 00 | [Prerequisites & SQL Refresher](lessons/00_prerequisites_and_sql_refresher.md) | Window functions, CTEs, why they matter for dbt | No |
| 01 | [Analytics Engineering & dbt](lessons/01_analytics_engineering_and_dbt.md) | What analytics engineering is, what dbt does, ETL vs ELT | No |
| 02 | [Environment Setup](lessons/02_environment_setup.md) | Install DuckDB, dbt-core, configure profiles.yml, ingest data | **Yes** |
| 03 | [Project Structure](lessons/03_project_structure.md) | Understand every file and folder in a dbt project | **Yes** |
| 04 | [Sources & Staging Models](lessons/04_sources_and_staging_models.md) | Define sources, build your first staging models | **Yes** |
| 05 | [Intermediate Models](lessons/05_intermediate_models.md) | Union datasets, handle schema mismatches, ref() vs source() | **Yes** |
| 06 | [Seeds & Macros](lessons/06_seeds_and_macros.md) | Load CSV lookup data, write reusable SQL with Jinja macros | **Yes** |
| 07 | [Marts: Fact & Dimension Tables](lessons/07_marts_fact_and_dimension_tables.md) | Build a star schema with fct_and dim_ tables, incremental models | **Yes** |
| 08 | [Tests & Data Quality](lessons/08_tests_and_data_quality.md) | Generic tests, singular tests, source freshness, model contracts | **Yes** |
| 09 | [Documentation](lessons/09_documentation.md) | Document models/columns in YAML, generate and serve docs | **Yes** |
| 10 | [Packages](lessons/10_packages.md) | Install dbt-utils, use surrogate keys and other utilities | **Yes** |
| 11 | [Commands Reference](lessons/11_commands_reference.md) | Every dbt command and flag you need to know | Reference |
| 12 | [Homework](lessons/12_homework.md) | Test your knowledge — queries, concepts, and build FHV staging model | **Yes** |

## Project structure

```
analytics_engineering/
├── README.md                 ← You are here
├── lessons/                  ← Step-by-step tutorial
├── scripts/
│   └── ingest_data.py        ← Downloads and loads taxi data into DuckDB
├── pyproject.toml            ← Python dependencies (managed by uv)
├── dbt_project.yml           ← dbt project configuration
├── packages.yml              ← Third-party dbt packages
├── .gitignore
├── models/
│   ├── staging/              ← 1:1 cleaned copies of raw tables
│   ├── intermediate/         ← Unions, enrichment, deduplication
│   └── marts/                ← Final star schema (fact + dimension tables)
│       └── reporting/        ← Aggregated reporting models
├── macros/                   ← Reusable SQL functions
├── seeds/                    ← CSV lookup tables
├── tests/                    ← Custom singular tests
├── snapshots/                ← SCD Type 2 change tracking (snap_zones example)
└── analyses/                 ← Ad-hoc SQL scripts
```

## Quick start (if you want to run the finished project)

If you want to skip the lessons and just run the completed project:

```bash
# 1. Install uv (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install dependencies
cd analytics_engineering
uv sync

# 3. Configure your dbt profile (see Lesson 02 for details)
# Add the profile from lessons/02_environment_setup.md to ~/.dbt/profiles.yml

# 4. Ingest data (add --fhv if you want FHV data for homework Q6)
uv run python scripts/ingest_data.py

# 5. Install dbt packages
uv run dbt deps

# 6. Load seed data
uv run dbt seed --target prod

# 7. Build everything
uv run dbt build --target prod
```

But the real value is in working through the lessons. Start with [Lesson 00](lessons/00_prerequisites_and_sql_refresher.md).

## How to use this tutorial

1. **Read the lesson** — understand the concept before typing anything
2. **Do the hands-on exercise** — create the files yourself, don't just copy-paste
3. **Run the verification step** — make sure it actually works
4. **Check the project files** — if you get stuck, the completed files in this project are your answer key
5. **Move to the next lesson** — each one builds on the previous
