# Lesson 01: Analytics Engineering & dbt

This lesson covers the "why" before the "how." No hands-on work here — just the mental models you need before building anything.

---

## The gap that created analytics engineering

A few shifts in the data world happened at roughly the same time:

- **Cloud data warehouses** (BigQuery, Snowflake, Redshift) made storage and compute cheap. You no longer need to be surgical about what data you load.
- **EL tools** (Fivetran, Stitch) automated the extract-and-load steps. Getting data into the warehouse became trivial.
- **SQL-first BI tools** (Looker, Mode) brought version control and self-service analytics.

This created a gap. **Data engineers** build great infrastructure but aren't always close to how the business uses the data. **Data analysts** understand the business but weren't trained in software engineering. **Nobody was bridging that gap.**

### The analytics engineer

The analytics engineer is the bridge. They bring software engineering best practices — version control, testing, documentation, modularity — into the transformation layer that sits between raw data and business consumption.

In the toolchain:

- **Data loading** → Fivetran, Stitch (the EL layer)
- **Data storing** → Cloud data warehouses
- **Data modeling** → **dbt** (this is where we'll spend our time)
- **Data presentation** → BI tools (Looker, Tableau, etc.)

---

## ETL vs ELT

Two philosophies for getting data ready:

**ETL (Extract → Transform → Load)**: Transform data *before* it hits the warehouse. Clean data from day one, but slower to set up.

**ELT (Extract → Load → Transform)**: Load raw data first, transform it *inside* the warehouse. Faster, more flexible. This is what cloud warehouses made possible — storage is cheap, so load everything and figure out transformations later.

**ELT is the dominant approach now, and dbt is the "T" in ELT.** It runs transformations inside the warehouse using SQL.

---

## What is dbt?

dbt (data build tool) is a transformation workflow tool. You write SQL SELECT statements, and dbt handles:

1. **Compiling** — resolves Jinja templates, `ref()` calls, `source()` calls
2. **Executing** — sends compiled SQL to your warehouse
3. **Materializing** — creates the result as a table, view, or incremental table
4. **Dependency management** — figures out what order to run things in
5. **Testing** — validates data quality automatically
6. **Documentation** — generates docs from your code

You never write `CREATE TABLE` yourself. You write a `SELECT`, and dbt wraps it in the right DDL/DML.

### What problems it solves

The transformation step has always existed. What dbt adds is **software engineering best practices for analytics code**:

- **Version control** — transformations live in git
- **Modularity** — break complex logic into reusable pieces
- **Testing** — automated data quality checks
- **Documentation** — generated from code, not a separate wiki
- **Environments** — separate dev and prod
- **CI/CD** — automated deployments

---

## dbt Core vs dbt Cloud

| | dbt Core | dbt Cloud |
|---|---------|-----------|
| **Cost** | Free, open source | SaaS (free tier available) |
| **Installation** | Local (pip install) | Web-based |
| **IDE** | Your editor (VS Code) | Web IDE or Cloud CLI |
| **Orchestration** | DIY (Airflow, cron) | Built-in scheduler |
| **Docs hosting** | DIY | Automatic |

**This tutorial uses dbt Core + DuckDB** because:

- It forces you to understand what's actually happening under the hood
- dbt Cloud abstracts a lot away — understanding Core first makes Cloud easy to pick up later
- Everything you learn transfers directly to dbt Cloud

---

## Dimensional Modeling (Kimball)

This is the mental model for how we'll structure our data. The goal: make data **understandable to business users** and **queries fast**.

### Fact tables vs Dimension tables

- **Fact tables** — measurements, metrics, events. Think **verbs**: "a trip happened." One row per event. Prefixed with `fct_`.
- **Dimension tables** — context around facts. Think **nouns**: "who, what, where." Prefixed with `dim_`.

Together they form a **star schema**: the fact table in the center, dimension tables around it.

### The Kitchen Analogy

Kimball uses a restaurant analogy that maps directly to our dbt project:

| Restaurant | Data Warehouse | Our dbt project |
|-----------|---------------|-----------------|
| **Pantry** (raw ingredients) | Staging area | `models/staging/` |
| **Kitchen** (cooking) | Processing area | `models/intermediate/` |
| **Dining hall** (served dishes) | Presentation area | `models/marts/` |

The pantry has raw ingredients (raw data). The kitchen is where the cooking happens (transformations). The dining hall is what customers see (final tables for dashboards).

### What we'll build

```text
                    ┌─────────────┐
                    │  dim_zones  │
                    └──────┬──────┘
                           │
┌──────────────┐    ┌──────┴──────┐    ┌───────────────┐
│ dim_vendors  │────│  fct_trips  │────│ payment_type  │
└──────────────┘    └──────┬──────┘    │   (seed)      │
                           │           └───────────────┘
                    ┌──────┴──────┐
                    │  fct_monthly│
                    │ zone_revenue│
                    └─────────────┘
```

---

## Self-check

1. What's the difference between ETL and ELT? Which does dbt support?
2. What are the two types of tables in a star schema?
3. What are the three layers in a dbt project, and what does each one contain?
4. Why does this tutorial use dbt Core instead of dbt Cloud?

---

**Next: [Lesson 02 — Environment Setup](02_environment_setup.md)**
