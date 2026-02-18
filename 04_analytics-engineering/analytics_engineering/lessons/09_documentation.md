# Lesson 09: Documentation

You've been writing documentation all along — every `description:` field in your YAML files is documentation. This lesson shows you how to generate a browsable website from it and why it matters.

---

## Where documentation lives

You've already been documenting in YAML files:

| File | What it documents |
|------|------------------|
| `sources.yml` | Source tables and their columns |
| `schema.yml` (per directory) | Models and their columns |
| `seeds_properties.yml` | Seed files |
| `macros_properties.yml` | Macros and their arguments |

The convention is one `schema.yml` per directory. Some teams prefer one YAML file per model (e.g., `stg_green_tripdata.yml`) — that works too, especially for large projects.

---

## What you can document

### Models and columns

```yaml
models:
  - name: fct_trips
    description: >
      Fact table containing all taxi trips from both yellow and green taxis.
      Each row represents a single trip with identifiers, locations,
      timestamps, trip details, and payment information.
    columns:
      - name: trip_id
        description: Unique trip identifier (surrogate key)
      - name: service_type
        description: Type of taxi service (Green or Yellow)
```

### Multi-line descriptions

Use `>` (folds newlines into spaces) or `|` (preserves newlines):

```yaml
description: >
  This is a long description that spans
  multiple lines but renders as a single paragraph.

description: |
  This description preserves
  line breaks exactly as written.
```

### Meta tags

Attach arbitrary metadata to any column or model:

```yaml
columns:
  - name: vendor_id
    description: Taxi technology provider
    meta:
      owner: data-engineering-team
      pii: false
      importance: high
```

Meta tags don't affect how dbt runs. They're for governance, discoverability, and team communication.

---

## Hands-on: Generate and serve docs

### Step 1: Generate the documentation

```bash
uv run dbt docs generate
```

This compiles everything — your YAML descriptions, model SQL, and metadata — into JSON files in `target/`.

### Step 2: Serve the docs locally

```bash
uv run dbt docs serve
```

This starts a local web server (default: `localhost:8080`). Open it in your browser.

### Step 3: Explore the docs site

The docs site shows you:

1. **Model code** — both the Jinja version you wrote and the compiled SQL
2. **Column details** — types, descriptions, tests
3. **Lineage graph** — a visual DAG showing the full path from sources to marts

Click on any model to see its details. Click the lineage graph icon (bottom-right) to see how everything connects.

### Step 4: Explore the lineage graph

The lineage graph is one of the most useful features. It shows:

- **Sources** (green nodes) — your raw data
- **Models** (blue nodes) — your transformations
- **Seeds** (yellow nodes) — your CSV files
- **Tests** — attached to each model

You can click on any node to focus on it and see its upstream and downstream dependencies.

---

## Documentation best practices

1. **Write descriptions as you build** — don't save it for later. The YAML files are right there.
2. **Focus on "what" and "why"** — the SQL shows "how." Your description should explain what a model represents and why it exists.
3. **Document assumptions** — if you filtered something or made a business decision, note it.
4. **Use meta tags for governance** — flag PII, ownership, and criticality.
5. **Keep it accurate** — outdated docs are worse than no docs. If you change a model, update the description.

---

## dbt Core vs dbt Cloud for docs

| | dbt Core | dbt Cloud |
|---|---------|-----------|
| Generate | `uv run dbt docs generate` (manual) | Automatic (checkbox in job settings) |
| Serve | `uv run dbt docs serve` (local only) | Hosted automatically |
| Sharing | DIY hosting (S3, Netlify, etc.) | Built-in |

For dbt Core, if you want others to see the docs, you'll need to host the generated `target/` files somewhere. For personal learning, `uv run dbt docs serve` is plenty.

---

## What you learned

- Documentation lives in the YAML files you've already been writing
- `uv run dbt docs generate` compiles it into a browsable website
- `uv run dbt docs serve` hosts it locally
- The lineage graph visually shows your entire DAG
- Meta tags add governance metadata without affecting runtime
- Document as you build, not after

---

**Next: [Lesson 10 — Packages](10_packages.md)**
