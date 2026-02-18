"""
Download and ingest NYC taxi trip data into DuckDB.

Downloads yellow and green taxi data (2019-2020) and FHV data (2019)
from the DataTalksClub repository, converts CSV.gz files to Parquet,
and loads them into a DuckDB database for use with dbt.

Usage:
    cd analytics_engineering
    python scripts/ingest_data.py          # yellow + green only
    python scripts/ingest_data.py --fhv    # also download FHV data (for homework Q6)
"""

import argparse
import duckdb
import requests
from pathlib import Path

BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download"


def download_and_convert_files(taxi_type, years):
    data_dir = Path("data") / taxi_type
    data_dir.mkdir(exist_ok=True, parents=True)

    for year in years:
        for month in range(1, 13):
            parquet_filename = f"{taxi_type}_tripdata_{year}-{month:02d}.parquet"
            parquet_filepath = data_dir / parquet_filename

            if parquet_filepath.exists():
                print(f"Skipping {parquet_filename} (already exists)")
                continue

            csv_gz_filename = f"{taxi_type}_tripdata_{year}-{month:02d}.csv.gz"
            csv_gz_filepath = data_dir / csv_gz_filename

            print(f"Downloading {csv_gz_filename}...")
            response = requests.get(
                f"{BASE_URL}/{taxi_type}/{csv_gz_filename}", stream=True
            )
            response.raise_for_status()

            with open(csv_gz_filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Converting {csv_gz_filename} to Parquet...")
            con = duckdb.connect()
            con.execute(
                f"""
                COPY (SELECT * FROM read_csv_auto('{csv_gz_filepath}'))
                TO '{parquet_filepath}' (FORMAT PARQUET)
            """
            )
            con.close()

            csv_gz_filepath.unlink()
            print(f"Completed {parquet_filename}")


def main():
    parser = argparse.ArgumentParser(description="Download and ingest NYC taxi data")
    parser.add_argument(
        "--fhv",
        action="store_true",
        help="Also download FHV (For-Hire Vehicle) data for 2019 (needed for homework Q6)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("NYC Taxi Data Ingestion")
    print("=" * 60)

    datasets = [
        ("yellow", [2019, 2020]),
        ("green", [2019, 2020]),
    ]
    if args.fhv:
        datasets.append(("fhv", [2019]))

    for taxi_type, years in datasets:
        print(f"\nProcessing {taxi_type} taxi data...")
        download_and_convert_files(taxi_type, years)

    print("\nLoading data into DuckDB...")
    db_path = "analytics_engineering.duckdb"
    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS prod")

    for taxi_type, _ in datasets:
        print(f"  Loading {taxi_type}_tripdata...")
        con.execute(
            f"""
            CREATE OR REPLACE TABLE prod.{taxi_type}_tripdata AS
            SELECT * FROM read_parquet('data/{taxi_type}/*.parquet', union_by_name=true)
        """
        )
        row_count = con.execute(
            f"SELECT count(*) FROM prod.{taxi_type}_tripdata"
        ).fetchone()[0]
        print(f"  Loaded {row_count:,} rows into prod.{taxi_type}_tripdata")

    con.close()

    print(f"\nDone! Database created at: {db_path}")
    print("You can now run: dbt debug")


if __name__ == "__main__":
    main()
