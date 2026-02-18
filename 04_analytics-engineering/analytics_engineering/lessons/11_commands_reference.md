# Lesson 11: Commands Reference

A complete reference for every dbt command and flag you'll use. Bookmark this one.

---

## Setup commands (run once or as needed)

| Command | What it does |
|---------|-------------|
| `uv run dbt init` | Creates a new dbt project from scratch |
| `uv run dbt debug` | Checks profiles.yml validity and warehouse connection |
| `uv run dbt deps` | Installs packages from packages.yml |
| `uv run dbt clean` | Deletes `target/` and `dbt_packages/` (run `uv run dbt deps` after) |

---

## Feature-specific commands

| Command | What it does |
|---------|-------------|
| `uv run dbt seed` | Loads all CSVs from `seeds/` into the database |
| `uv run dbt snapshot` | Runs snapshot definitions (SCD Type 2 tracking) |
| `uv run dbt source freshness` | Checks if source data is stale |
| `uv run dbt docs generate` | Compiles documentation into JSON |
| `uv run dbt docs serve` | Starts a local docs website (localhost:8080) |

---

## The daily drivers

### uv run dbt compile

Resolves all Jinja and outputs pure SQL to `target/compiled/`. Nothing hits the database. **Free** — no compute cost. Use it to:

- Catch Jinja errors fast
- Inspect the SQL that dbt would actually run
- Verify `ref()` and `source()` resolve correctly

```bash
uv run dbt compile
uv run dbt compile --select stg_green_tripdata
```

### dbt run

Materializes every model (or selected models) in your project.

```bash
uv run dbt run                                    # everything
uv run dbt run --select stg_green_tripdata        # one model
uv run dbt run --select models/staging            # one directory
uv run dbt run --target prod                      # against production
```

### dbt test

Runs all tests (generic, singular, unit). Reports pass/fail. Doesn't build anything.

```bash
uv run dbt test
uv run dbt test --select fct_trips
```

### dbt build (the most important command)

Smart combination of `dbt run` + `dbt test` + `dbt seed` + `dbt snapshot`, all DAG-aware. If something fails, it skips everything downstream.

```bash
uv run dbt build                                  # everything
uv run dbt build --select +fct_trips              # fct_trips + all upstream
uv run dbt build --target prod                    # against production
```

### dbt retry

Re-runs from the point of failure. Reads `target/run_results.json` from the last command and re-executes only failed/skipped nodes.

```bash
uv run dbt retry
```

### dbt show

Previews model output without materializing. Great for quick checks.

```bash
uv run dbt show --select stg_green_tripdata --limit 5
uv run dbt show --inline "select count(*) from {{ ref('fct_trips') }}"
```

---

## Important flags

### --full-refresh / -f

Drops and rebuilds incremental models from scratch. Use when historical data changed or you suspect duplicates.

```bash
uv run dbt run --full-refresh --select fct_trips
uv run dbt build --full-refresh
```

### --fail-fast

Stops execution on the first failure instead of continuing. Good for CI.

```bash
uv run dbt build --fail-fast
```

### --target / -t

Overrides which profile target to use (default is `dev`).

```bash
uv run dbt run --target prod
uv run dbt build --target prod
```

### --select / -s

Runs only specific models. Multiple selection methods:

**By model name:**

```bash
uv run dbt run --select stg_green_tripdata
```

**By directory:**

```bash
uv run dbt run --select models/staging
```

**By tag:**

```bash
uv run dbt run --select tag:nightly
```

**With graph operators (the + sign):**

```bash
# Model + all upstream dependencies
uv run dbt run --select +fct_trips

# Model + all downstream dependents
uv run dbt run --select fct_trips+

# Both directions
uv run dbt run --select +fct_trips+
```

| Pattern | What it selects |
|---------|----------------|
| `+model` | model + everything upstream (ancestors) |
| `model+` | model + everything downstream (descendants) |
| `+model+` | everything upstream + model + everything downstream |

**With state selectors (CI/CD):**

```bash
uv run dbt build --select state:modified+ --state ./prod-artifacts
```

- `state:new` — only newly created files
- `state:modified` — anything changed since last run
- Add `+` to include downstream dependencies

---

## Command workflow examples

### Daily development

```bash
uv run dbt compile --select my_model       # check for Jinja errors (free)
uv run dbt run --select my_model           # build just what you changed
uv run dbt test --select my_model          # test just what you changed
```

### Full project build

```bash
uv run dbt deps                            # install/update packages
uv run dbt seed                            # load seed data
uv run dbt build --target prod             # build + test everything
```

### After a failure

```bash
uv run dbt retry                           # pick up where it failed
```

### Full refresh (monthly maintenance)

```bash
uv run dbt build --full-refresh --target prod
```

### Generate and view documentation

```bash
uv run dbt docs generate
uv run dbt docs serve                      # opens localhost:8080
```

---

## What you learned

- `dbt build` is the most important command — it runs seeds, models, snapshots, and tests in dependency order
- `dbt compile` is your fast feedback loop — catches errors with zero warehouse cost
- The `+` operator in `--select` pulls in upstream or downstream dependencies
- `--full-refresh` rebuilds incremental models from scratch
- `--target prod` runs against production instead of dev
- `dbt retry` picks up where a failed run left off

---

## You've completed the core tutorial

One more step: put your knowledge to the test with the homework.

**Next: [Lesson 12 — Homework](12_homework.md)**

After the homework, some ideas for further exploration:

- Add a singular test for negative fare amounts
- Create a new reporting model (e.g., trips by hour of day)
- Try running `dbt build --full-refresh --target prod` to build the complete dataset
- Explore the generated docs site and lineage graph
- Look into dbt-expectations for more advanced tests
