# Module 5: Data Platforms

## Overview

In this module, you'll learn about data platforms - tools that help you manage the entire data lifecycle from ingestion to analytics.

We'll use [Bruin](https://getbruin.com/) as an example of a data platform. Bruin puts multiple tools under one platform:

- Data ingestion (extract from sources to your warehouse)
- Data transformation (cleaning, modeling, aggregating)
- Data orchestration (scheduling and dependency management)
- Data quality (built-in checks and validation)
- Metadata management (lineage, documentation)

## Tutorial

Follow the complete hands-on tutorial at:

[Bruin Data Engineering Zoomcamp Template](https://github.com/bruin-data/bruin/tree/main/templates/zoomcamp)

The template is a TODO-based learning exercise — run `bruin init zoomcamp my-taxi-pipeline` and fill in the configuration and code guided by inline comments. The [notes](notes/) contain completed reference implementations.

## Videos

### 5.1 - Introduction to Bruin

<https://youtu.be/f6vg7lGqZx0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=1>

Introduction to the Bruin data platform: what it is, what a modern data stack looks like (ETL/ELT, orchestration, data quality), and how Bruin brings all of these together into a single project.

- [Notes](notes/01-introduction.md)

### 5.2 - Getting Started with Bruin

<https://youtu.be/JJwHKSidX_c&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=2>

Install Bruin, set up the VS Code/Cursor extension and Bruin MCP, and create a first project using `bruin init`. Walk through environments, connections (DuckDB, Chess.com), pipeline YAML configuration, and running Python, YAML ingestor, and SQL assets.

- [Notes](notes/02-getting-started.md)

### 5.3 - Building an End-to-End Pipeline with NYC Taxi Data

<https://youtu.be/q0k_iz9kWsI&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=3>

Build a full pipeline with a three-layered architecture (ingestion, staging, reports) using NYC taxi data and DuckDB.

- [Notes](notes/03-nyc-taxi-pipeline.md)

### 5.4 - Using Bruin MCP with AI Agents

<https://youtu.be/224xH7h8OaQ&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=4>

Install the Bruin MCP in Cursor/VS Code and use an AI agent to build the entire NYC taxi pipeline end to end. Query data conversationally, ask questions about pipeline logic, and troubleshoot issues — all through natural language.

- [Notes](notes/04-bruin-mcp.md)

### :movie_camera: 5.5 - Deploying to Bruin Cloud

<https://youtu.be/uBqjLEwF8rc&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=5>

Register for Bruin Cloud, connect your GitHub repository, set up data warehouse connections, deploy and monitor your pipelines with a fully managed infrastructure.

- [Notes](notes/05-bruin-cloud.md)

## Bruin Core Concepts

Short videos covering the fundamental concepts of Bruin: projects, pipelines, assets, variables, and commands.

### :movie_camera: Projects

<https://www.youtube.com/watch?v=YWDjnSxbBtY>

The root directory where you create your Bruin data pipeline. Learn about project initialization, the `.bruin.yml` configuration file, environments, and connections.

- [Notes](notes/06-core-01-projects.md)

### :movie_camera: Pipelines

<https://www.youtube.com/watch?v=uzp_DiR4Sok>

A grouping mechanism for organizing assets based on their execution schedule. Each pipeline has a single schedule and its own configuration file.

- [Notes](notes/06-core-02-pipelines.md)

### :movie_camera: Assets

<https://www.youtube.com/watch?v=ZElY5SoqrwI>

Single files that perform specific tasks, creating or updating tables/views in your database. Covers SQL, Python, and YAML asset types with examples.

- [Notes](notes/06-core-03-assets.md)

### :movie_camera: Variables

<https://www.youtube.com/watch?v=XCx0nDmhhxA>

Dynamic values initialized at each pipeline run. Learn about built-in variables (start_date, end_date) and custom variables for parameterizing your pipelines.

- [Notes](notes/06-core-04-variables.md)

### :movie_camera: Commands

<https://www.youtube.com/watch?v=3nykPEs_V7E>

CLI commands for interacting with your Bruin project: `bruin run`, `bruin validate`, `bruin lineage`, and more with practical examples.

- [Notes](notes/06-core-05-commands.md)# Validate first
  bruin validate ./pipeline/pipeline.yml

## Run one month

bruin run ./pipeline/pipeline.yml --start-date 2019-01-01 --end-date 2019-01-31

## Or full refresh (wipes and rebuilds everything)

bruin run ./pipeline/pipeline.yml --full-refresh

## Query results

```bash
bruin query --connection duckdb-default --query "SELECT COUNT(*) FROM ingestion.trips"
bruin query --connection duckdb-default --query "SELECT * FROM reports.trips_report LIMIT 10"
```

## Project structure

```text
bruin-taxi-pipeline/
├── .bruin.yml                              # DuckDB connection (local only, gitignored)
├── pipeline/
│   ├── pipeline.yml                        # Schedule, variables (taxi_types)
│   └── assets/
│       ├── ingestion/
│       │   ├── trips.py                    # Fetches parquet from NYC TLC API
│       │   ├── payment_lookup.asset.yml    # Seed CSV → DuckDB
│       │   ├── payment_lookup.csv
│       │   └── requirements.txt
│       ├── staging/
│       │   └── trips.sql                   # Join + dedup + time_interval
│       └── reports/
│           └── trips_report.sql            # Aggregate by date/type/payment
└── issues/
    └── README.md                           # Gotchas encountered
```

## Key things to remember

- `.bruin.yml` must live in the project root (not the git root) — `bruin init` puts it in the wrong place
- `append` strategy in ingestion means duplicate rows on re-runs — staging deduplicates, or use `--full-refresh`
- `--var 'taxi_types=["yellow","green"]'` to override pipeline variables
- `bruin run <asset-path> --downstream` to run an asset plus everything after it
- DuckDB file lands at `pipeline/nyc_taxi.duckdb`

## Resources

- [Bruin Documentation](https://getbruin.com/docs)
- [Bruin GitHub Repository](https://github.com/bruin-data/bruin)
- [Bruin MCP (AI Integration)](https://getbruin.com/docs/bruin/getting-started/bruin-mcp)
- [Bruin Cloud](https://getbruin.com/) — managed deployment and monitoring

## Homework

- [homework.md](homework.md) — 7 multiple-choice questions (all conceptual, no code needed)
