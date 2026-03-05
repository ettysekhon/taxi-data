"""Transport for London (TfL) Unified API – dlt REST API source.

API docs: https://api.tfl.gov.uk/
Most endpoints work without auth. Supply app_id/app_key (from secrets.toml)
for higher rate limits and access to restricted endpoints like AccidentStats.
"""

from typing import Any, List, Optional

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


@dlt.source
def tfl_rest_source(
    app_id: Optional[str] = dlt.secrets.value,
    app_key: Optional[str] = dlt.secrets.value,
    base_url: str = "https://api.tfl.gov.uk",
) -> Any:
    """TfL Unified API source — loads reference data, live status, and accident stats."""
    params: dict = {}
    if app_id and app_key:
        params = {"app_id": app_id, "app_key": app_key}

    config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
            "paginator": "single_page",
        },
        "resource_defaults": {
            "endpoint": {
                "params": params,
            },
        },
        "resources": [
            {
                "name": "accident_stats",
                "endpoint": {
                    "path": "AccidentStats/{year}",
                    "params": {"year": 2019},
                },
            },
            "AirQuality",
            "BikePoint",
            "Road",
            {
                "name": "line_modes",
                "endpoint": {"path": "Line/Meta/Modes"},
            },
            {
                "name": "line_severity",
                "endpoint": {"path": "Line/Meta/Severity"},
            },
            {
                "name": "line_by_mode",
                "endpoint": {
                    "path": "Line/Mode/{modes}",
                    "params": {"modes": "tube,dlr,overground"},
                },
            },
            {
                "name": "line_route",
                "endpoint": {"path": "Line/Route"},
            },
            {
                "name": "line_status",
                "endpoint": {
                    "path": "Line/{ids}/Status",
                    "params": {
                        "ids": "victoria,circle,central,northern",
                        "detail": False,
                    },
                },
            },
            {
                "name": "journey_modes",
                "endpoint": {"path": "Journey/Meta/Modes"},
            },
            {
                "name": "active_service_types",
                "endpoint": {"path": "Mode/ActiveServiceTypes"},
            },
            {
                "name": "stop_point_types",
                "endpoint": {"path": "StopPoint/Meta/StopTypes"},
            },
            {
                "name": "stop_point_modes",
                "endpoint": {"path": "StopPoint/Meta/Modes"},
            },
        ],
    }
    return rest_api_resources(config)


@dlt.source
def tfl_rest_source_with_params(
    app_id: Optional[str] = dlt.secrets.value,
    app_key: Optional[str] = dlt.secrets.value,
    base_url: str = "https://api.tfl.gov.uk",
    accident_year: int = 2019,
    line_ids: Optional[List[str]] = None,
    line_modes: str = "tube,dlr,overground",
) -> Any:
    """TfL source with configurable parameters for use from config or CLI."""
    line_ids = line_ids or ["victoria", "circle", "central", "northern"]
    params: dict = {}
    if app_id and app_key:
        params = {"app_id": app_id, "app_key": app_key}

    config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
            "paginator": "single_page",
        },
        "resource_defaults": {
            "endpoint": {
                "params": params,
            },
        },
        "resources": [
            {
                "name": "accident_stats",
                "endpoint": {
                    "path": "AccidentStats/{year}",
                    "params": {"year": accident_year},
                },
            },
            "AirQuality",
            "BikePoint",
            "Road",
            {
                "name": "line_by_mode",
                "endpoint": {
                    "path": "Line/Mode/{modes}",
                    "params": {"modes": line_modes},
                },
            },
            {
                "name": "line_status",
                "endpoint": {
                    "path": "Line/{ids}/Status",
                    "params": {
                        "ids": ",".join(line_ids),
                        "detail": False,
                    },
                },
            },
        ],
    }
    return rest_api_resources(config)


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="tfl_rest",
        destination="duckdb",
        dataset_name="tfl",
    )
    load_info = pipeline.run(tfl_rest_source())
    print(load_info)
