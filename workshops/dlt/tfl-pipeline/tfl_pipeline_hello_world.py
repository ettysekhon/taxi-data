import dlt

data = [
    {"name": "Kings Cross", "zone": 1, "lines": ["Northern", "Piccadilly", "Victoria"]},
    {"name": "Bank", "zone": 1, "lines": ["Central", "Northern", "Waterloo & City"]},
    {"name": "Stratford", "zone": 3, "lines": ["Central", "Jubilee"]},
]

pipeline = dlt.pipeline(
    pipeline_name="hello_pipeline",
    destination="duckdb",
    dataset_name="tube_data",
)

load_info = pipeline.run(data, table_name="stations")
print(load_info)
