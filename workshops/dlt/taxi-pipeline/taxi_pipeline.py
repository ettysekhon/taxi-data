import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


@dlt.source
def taxi_api_source():
    """NYC Yellow Taxi trip data — dlt pipeline.

    Loads paginated JSON from the DE Zoomcamp API into DuckDB.
    API returns 1,000 records per page; stops when an empty page is returned.
    """
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net",
            "paginator": {
                "type": "page_number",
                "base_page": 1,
                "page_param": "page",
                "total_path": None,
                "maximum_page": 50,
            },
        },
        "resources": [
            {
                "name": "rides",
                "endpoint": {
                    "path": "data_engineering_zoomcamp_api",
                },
                "write_disposition": "replace",
            },
        ],
    }
    yield from rest_api_resources(config)


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="taxi_pipeline",
        destination="duckdb",
        dataset_name="taxi_data",
    )
    load_info = pipeline.run(taxi_api_source())
    print(load_info)
