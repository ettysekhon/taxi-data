# Issues Faced

## 1. `.bruin.yml` created at git repo root

`bruin init` walks up to the git root and places `.bruin.yml` there. Had to manually move it into `bruin-taxi-pipeline/`.

## 2. Duplicate rows in `ingestion.trips` after multiple runs

The `append` strategy adds rows on every run without deduplication. Running the pipeline twice for the same date range doubles the ingestion row count. Not a problem — `staging.trips` deduplicates with `QUALIFY ROW_NUMBER()`. Use `--full-refresh` to reset if needed.

## 3. Catalog Error on first run with `delete+insert` / `time_interval`

`time_interval` tries to DELETE from the target before inserting. On the first run the table doesn't exist yet, causing a catalog error. Bruin handles this automatically on subsequent runs once the table is created by the first successful run.
