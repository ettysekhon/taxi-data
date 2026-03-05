import dlt
from dlt.sources.rest_api import rest_api_source

source = rest_api_source(
    {
        "client": {
            "base_url": "https://api.tfl.gov.uk",
        },
        "resource_defaults": {
            "primary_key": "id",
            "write_disposition": "replace",
        },
        "resources": [
            {
                "name": "bike_points",
                "endpoint": {
                    "path": "BikePoint",
                },
            },
        ],
    }
)

pipeline = dlt.pipeline(
    pipeline_name="tfl_pipeline",
    destination="duckdb",
    dataset_name="tfl_data",
)

load_info = pipeline.run(source)
print(load_info)
