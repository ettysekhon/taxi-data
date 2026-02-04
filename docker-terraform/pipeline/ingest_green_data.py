import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')

# Load green taxi data (parquet)
df = pd.read_parquet('green_tripdata_2025-11.parquet')
df.to_sql('green_taxi_trips', engine, if_exists='replace', index=False)
print(f'Loaded {len(df)} green taxi trips')

# Load zones
zones = pd.read_csv('taxi_zone_lookup.csv')
zones.to_sql('zones', engine, if_exists='replace', index=False)
print(f'Loaded {len(zones)} zones')