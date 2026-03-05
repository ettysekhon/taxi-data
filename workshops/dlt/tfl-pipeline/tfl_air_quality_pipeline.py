import dlt
from dlt.sources.rest_api import rest_api_source

source = rest_api_source(
    {
        "client": {
            "base_url": "https://api.tfl.gov.uk",
        },
        "resources": [
            {
                "name": "air_quality",
                "endpoint": {
                    "path": "AirQuality",
                    "data_selector": "currentForecast",
                },
                "write_disposition": "replace",
            },
        ],
    }
)

pipeline = dlt.pipeline(
    pipeline_name="tfl_air_pipeline",
    destination="duckdb",
    dataset_name="tfl_air_data",
)

load_info = pipeline.run(source)
print(load_info)
