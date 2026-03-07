# Module 6: Batch Processing — Progress

## Environment

| Component       | Version    | Notes                                          |
| --------------- | ---------- | ---------------------------------------------- |
| PySpark         | 4.1.1      | Bundled Spark, no separate `SPARK_HOME` needed |
| Java            | OpenJDK 17 | Installed via `brew install openjdk@17`        |
| Python          | 3.12       | Managed by `uv`                                |
| Package manager | `uv`       | `pyproject.toml` in `code/`                    |

## Setup completed

- Installed Java 17 via Homebrew, `JAVA_HOME` set in `.zshrc`
- Created `code/pyproject.toml` with `pyspark>=4.0.0`, `jupyter`, `pandas`
- Ran `uv sync` — PySpark 4.1.1 installed and verified working
- Cleaned up legacy Spark 3.x files:
  - `setup/config/spark.dockerfile` (used openjdk:11)
  - `setup/config/spark-defaults.conf` (hardcoded YARN/GCS paths)
  - `setup/config/core-site.xml` (hardcoded GCS credentials)
  - `setup/hadoop-yarn.md` (Hadoop 3.2.3 YARN setup)
  - `code/06_spark_sql.py` (auto-generated from notebook)
  - `code/06_spark_sql_big_query.py` (hardcoded GCS bucket names)

## Notebooks

All notebooks were authored on Spark 3.0.3. They run on Spark 4.x with minor changes:

- `registerTempTable()` is deprecated — use `createOrReplaceTempView()`
- `!wget` shell commands are Linux-specific — use `curl` or Python on macOS
- Download URLs may need updating (NYC TLC data moved from S3 to GitHub releases)

| #   | Notebook                | Topic                                 | Status  |
| --- | ----------------------- | ------------------------------------- | ------- |
| 03  | `03_test.ipynb`         | Hello world — read CSV, write Parquet | Done    |
| 04  | `04_pyspark.ipynb`      | Schema, repartition, filters, UDFs    | Done    |
| 05  | `05_taxi_schema.ipynb`  | Convert green/yellow CSV to Parquet   | Done    |
| 06  | `06_spark_sql.ipynb`    | Spark SQL — unions, revenue report    | Done    |
| 07  | `07_groupby_join.ipynb` | GroupBy internals, shuffle, joins     | Done    |
| 08  | `08_rdds.ipynb`         | RDDs (optional)                       | Done    |
| 09  | `09_spark_gcs.ipynb`    | GCS connector (cloud)                 | Skipped |
| HW  | `homework.ipynb`        | Homework questions (FHVHV Feb 2021)   | Done    |

## How to run

```bash
cd 06-batch/code
export JAVA_HOME=$(brew --prefix openjdk@17)
uv run jupyter notebook
```

## Spark 4.x vs 3.x — key differences for these exercises

- `SPARK_HOME` not needed — PySpark 4.x bundles everything
- Java 17 required (3.x used Java 8/11)
- `registerTempTable()` removed — use `createOrReplaceTempView()`
- `unionAll()` still works but `union()` is preferred
- Log4j2 replaces Log4j1 (different warning format, no impact on code)
