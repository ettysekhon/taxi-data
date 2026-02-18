# Lesson 02: Environment Setup

Time to get your hands dirty. By the end of this lesson you'll have DuckDB, dbt Core, and a database full of taxi data ready to transform.

We use **uv** for dependency management — it's faster than pip and handles virtual environments automatically.

---

## Step 1: Install uv

uv is a fast Python package and project manager written in Rust. It replaces pip, venv, and pyenv in one tool.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or if you prefer pip:

```bash
pip install uv
```

Verify:

```bash
uv --version
```

## Step 2: Install project dependencies

Navigate to the project directory and let uv install everything:

```bash
cd analytics_engineering
uv sync
```

This reads `pyproject.toml` and installs:

- **dbt-duckdb** — dbt Core + the DuckDB adapter
- **duckdb** — the DuckDB database engine
- **requests** — for downloading the taxi data

uv automatically creates a virtual environment in `.venv/` and pins exact versions in `uv.lock`.

Verify dbt is available:

```bash
uv run dbt --version
```

You should see dbt-core and dbt-duckdb listed.

> **Note on `uv run`**: This runs a command inside the virtual environment without you having to activate it. You can alternatively activate the venv with `source .venv/bin/activate` and then use `dbt` directly.

## Step 3: Configure your dbt profile

dbt needs to know *how* to connect to your database. This is configured in `~/.dbt/profiles.yml` — a file in your home directory (not in the project).

Create or edit `~/.dbt/profiles.yml`:

```yaml
analytics_engineering:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: analytics_engineering.duckdb
      schema: dev
      threads: 1
      extensions:
        - parquet
      settings:
        memory_limit: '2GB'
        preserve_insertion_order: false

    prod:
      type: duckdb
      path: analytics_engineering.duckdb
      schema: prod
      threads: 1
      extensions:
        - parquet
      settings:
        memory_limit: '2GB'
        preserve_insertion_order: false
```

### What each field means

| Field | Purpose |
|-------|---------|
| `analytics_engineering` | Profile name — must match `profile:` in `dbt_project.yml` |
| `target: dev` | Default target when you run `uv run dbt run` without `--target` |
| `type: duckdb` | Which adapter to use |
| `path` | Where the DuckDB database file lives (relative to where you run dbt) |
| `schema: dev` | Schema name — dev models go to `dev.*`, prod models to `prod.*` |
| `threads: 1` | How many models to build in parallel (keep at 1 for DuckDB to avoid memory issues) |
| `memory_limit` | How much RAM DuckDB can use. Adjust based on your machine (see troubleshooting below) |

### Memory settings by system RAM

| Your RAM | Recommended `memory_limit` |
|----------|---------------------------|
| 4 GB | `'1GB'` (consider using GitHub Codespaces instead) |
| 8 GB | `'2GB'` |
| 16+ GB | `'4GB'` |

## Step 4: Download and ingest the taxi data

From the project directory:

```bash
uv run python scripts/ingest_data.py
```

This script:

1. Downloads yellow and green taxi trip data (2019-2020) as compressed CSV files
2. Converts them to Parquet format (more efficient)
3. Creates a `prod` schema in DuckDB
4. Loads all the data into `prod.green_tripdata` and `prod.yellow_tripdata`

The download takes several minutes depending on your internet speed. The final DuckDB file will be ~1-2 GB.

> **For homework Q6**: Add the `--fhv` flag to also download For-Hire Vehicle data:

```bash
uv run python scripts/ingest_data.py --fhv
```

## Step 5: Verify the connection

```bash
uv run dbt debug
```

You should see all green checkmarks:

- `profiles.yml` found
- `dbt_project.yml` found
- Connection test passed

### Troubleshooting

**"Could not find profile"** — The profile name in `~/.dbt/profiles.yml` must exactly match the `profile:` field in `dbt_project.yml`. Ours is `analytics_engineering`.

**"Connection test failed"** — Make sure you ran the ingestion script first and that the `.duckdb` file exists in the project directory.

**Out of Memory errors** — Lower `memory_limit` in `profiles.yml`, close other applications, or see the [DuckDB troubleshooting guide](../../setup/duckdb_troubleshooting.md). Consider using GitHub Codespaces (free tier gives 8-16 GB RAM).

## Step 6: (Optional) Install VS Code extension

If you're using VS Code, install **dbt Power User by AltimateAI**:

1. Open Extensions (Cmd+Shift+X / Ctrl+Shift+X)
2. Search "dbt Power User"
3. Install **dbt Power User by AltimateAI**

This gives you SQL highlighting, auto-completion for `ref()` and `source()`, and inline lineage visualization.

> **Note**: The official dbt Labs extension requires dbt Fusion and doesn't support dbt Core with DuckDB. Use the community extension instead.

---

## What you accomplished

- Installed uv and all project dependencies (dbt-core, dbt-duckdb, DuckDB)
- Created a `profiles.yml` with dev and prod targets
- Loaded ~50 million taxi trip records into DuckDB
- Verified dbt can connect to your database

---

**Next: [Lesson 03 — Project Structure](03_project_structure.md)**
