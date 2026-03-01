"""@bruin
name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default

materialization:
  type: table
  strategy: append

columns:
  - name: pickup_datetime
    type: timestamp
    description: "When the meter was engaged"
  - name: dropoff_datetime
    type: timestamp
    description: "When the meter was disengaged"
  - name: pickup_location_id
    type: integer
    description: "TLC Taxi Zone where trip started"
  - name: dropoff_location_id
    type: integer
    description: "TLC Taxi Zone where trip ended"
  - name: fare_amount
    type: float
    description: "Time and distance fare"
  - name: payment_type
    type: integer
    description: "Payment method code"
  - name: taxi_type
    type: string
    description: "Type of taxi (yellow or green)"
@bruin"""

import os
import json
import ssl
import tempfile
import urllib.request
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


def materialize():
    start_date = datetime.strptime(os.environ["BRUIN_START_DATE"], "%Y-%m-%d")
    end_date = datetime.strptime(os.environ["BRUIN_END_DATE"], "%Y-%m-%d")
    taxi_types = json.loads(os.environ.get("BRUIN_VARS", "{}")).get("taxi_types", ["yellow"])

    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data"
    frames = []

    current = start_date.replace(day=1)
    while current <= end_date:
        year = current.strftime("%Y")
        month = current.strftime("%m")

        for taxi_type in taxi_types:
            url = f"{base_url}/{taxi_type}_tripdata_{year}-{month}.parquet"
            print(f"Fetching {url}")
            try:
                ssl_ctx = ssl.create_default_context()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl.CERT_NONE
                with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
                    with urllib.request.urlopen(url, context=ssl_ctx) as resp:
                        tmp.write(resp.read())
                    tmp_path = tmp.name
                df = pd.read_parquet(tmp_path)
                os.unlink(tmp_path)

                pickup_col = next((c for c in df.columns if "pickup_datetime" in c.lower()), None)
                dropoff_col = next((c for c in df.columns if "dropoff_datetime" in c.lower()), None)
                pu_loc = next((c for c in df.columns if c.lower() == "pulocationid"), None)
                do_loc = next((c for c in df.columns if c.lower() == "dolocationid"), None)

                result = pd.DataFrame({
                    "pickup_datetime": df[pickup_col] if pickup_col else None,
                    "dropoff_datetime": df[dropoff_col] if dropoff_col else None,
                    "pickup_location_id": df[pu_loc] if pu_loc else None,
                    "dropoff_location_id": df[do_loc] if do_loc else None,
                    "fare_amount": df.get("fare_amount"),
                    "payment_type": df.get("payment_type"),
                    "taxi_type": taxi_type,
                })
                result["extracted_at"] = datetime.utcnow()
                frames.append(result)
            except Exception as e:
                print(f"Skipping {url}: {e}")

        current += relativedelta(months=1)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)
