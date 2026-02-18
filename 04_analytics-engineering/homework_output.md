# Homework Output

Q1

```text
uv run dbt seed --target prod
17:10:34  Running with dbt=1.11.6
17:10:34  Registered adapter: duckdb=1.10.1
17:10:34  Unable to do partial parsing because config vars, config profile, or config target have changed
17:10:34  Unable to do partial parsing because profile has changed
17:10:35  Found 8 models, 1 snapshot, 2 seeds, 31 data tests, 3 sources, 620 macros
17:10:35  
17:10:35  Concurrency: 1 threads (target='prod')
17:10:35  
17:10:35  1 of 2 START seed file prod.payment_type_lookup ................................ [RUN]
17:10:35  1 of 2 OK loaded seed file prod.payment_type_lookup ............................ [INSERT 7 in 0.03s]
17:10:35  2 of 2 START seed file prod.taxi_zone_lookup ................................... [RUN]
17:10:35  2 of 2 OK loaded seed file prod.taxi_zone_lookup ............................... [INSERT 265 in 0.01s]
17:10:35  
17:10:35  Finished running 2 seeds in 0 hours 0 minutes and 0.14 seconds (0.14s).
17:10:35  
17:10:35  Completed successfully
17:10:35  
17:10:35  Done. PASS=2 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=2
```

```text
uv run dbt build --target prod
17:10:51  Running with dbt=1.11.6
17:10:51  Registered adapter: duckdb=1.10.1
17:10:51  Unable to do partial parsing because config vars, config profile, or config target have changed
17:10:51  Unable to do partial parsing because profile has changed
17:10:52  Found 8 models, 1 snapshot, 2 seeds, 31 data tests, 3 sources, 620 macros
17:10:52  
17:10:52  Concurrency: 1 threads (target='prod')
17:10:52  
17:10:52  1 of 42 START sql view model prod.stg_green_tripdata ........................... [RUN]
17:10:52  1 of 42 OK created sql view model prod.stg_green_tripdata ...................... [OK in 0.04s]
17:10:52  2 of 42 START sql view model prod.stg_yellow_tripdata .......................... [RUN]
17:10:52  2 of 42 OK created sql view model prod.stg_yellow_tripdata ..................... [OK in 0.01s]
17:10:52  3 of 42 START seed file prod.payment_type_lookup ............................... [RUN]
17:10:52  3 of 42 OK loaded seed file prod.payment_type_lookup ........................... [INSERT 7 in 0.03s]
17:10:52  4 of 42 START seed file prod.taxi_zone_lookup .................................. [RUN]
17:10:52  4 of 42 OK loaded seed file prod.taxi_zone_lookup .............................. [INSERT 265 in 0.01s]
17:10:52  5 of 42 START test not_null_stg_green_tripdata_pickup_datetime ................. [RUN]
17:10:52  5 of 42 PASS not_null_stg_green_tripdata_pickup_datetime ....................... [PASS in 0.02s]
17:10:52  6 of 42 START test not_null_stg_green_tripdata_vendor_id ....................... [RUN]
17:10:52  6 of 42 PASS not_null_stg_green_tripdata_vendor_id ............................. [PASS in 0.02s]
17:10:52  7 of 42 START test not_null_stg_yellow_tripdata_pickup_datetime ................ [RUN]
17:10:52  7 of 42 PASS not_null_stg_yellow_tripdata_pickup_datetime ...................... [PASS in 0.01s]
17:10:52  8 of 42 START test not_null_stg_yellow_tripdata_vendor_id ...................... [RUN]
17:10:53  8 of 42 PASS not_null_stg_yellow_tripdata_vendor_id ............................ [PASS in 0.14s]
17:10:53  9 of 42 START test not_null_payment_type_lookup_payment_type ................... [RUN]
17:10:53  9 of 42 PASS not_null_payment_type_lookup_payment_type ......................... [PASS in 0.01s]
17:10:53  10 of 42 START test unique_payment_type_lookup_payment_type .................... [RUN]
17:10:53  10 of 42 PASS unique_payment_type_lookup_payment_type .......................... [PASS in 0.01s]
17:10:53  11 of 42 START sql table model prod.dim_zones .................................. [RUN]
17:10:53  11 of 42 OK created sql table model prod.dim_zones ............................. [OK in 0.03s]
17:10:53  12 of 42 START snapshot snapshots.snap_zones ................................... [RUN]
17:10:53  12 of 42 OK snapshotted snapshots.snap_zones ................................... [OK in 0.10s]
17:10:53  13 of 42 START sql table model prod.int_trips_unioned .......................... [RUN]
17:11:05  13 of 42 OK created sql table model prod.int_trips_unioned ..................... [OK in 12.67s]
17:11:05  14 of 42 START test not_null_dim_zones_location_id ............................. [RUN]
17:11:05  14 of 42 PASS not_null_dim_zones_location_id ................................... [PASS in 0.02s]
17:11:05  15 of 42 START test unique_dim_zones_location_id ............................... [RUN]
17:11:05  15 of 42 PASS unique_dim_zones_location_id ..................................... [PASS in 0.02s]
17:11:05  16 of 42 START sql table model prod.int_trips .................................. [RUN]
17:13:42  16 of 42 OK created sql table model prod.int_trips ............................. [OK in 156.75s]
17:13:42  17 of 42 START test accepted_values_int_trips_service_type__Green__Yellow ...... [RUN]
17:13:42  17 of 42 PASS accepted_values_int_trips_service_type__Green__Yellow ............ [PASS in 0.32s]
17:13:42  18 of 42 START test not_null_int_trips_pickup_datetime ......................... [RUN]
17:13:43  18 of 42 PASS not_null_int_trips_pickup_datetime ............................... [PASS in 0.02s]
17:13:43  19 of 42 START test not_null_int_trips_service_type ............................ [RUN]
17:13:43  19 of 42 PASS not_null_int_trips_service_type .................................. [PASS in 0.01s]
17:13:43  20 of 42 START test not_null_int_trips_total_amount ............................ [RUN]
17:13:43  20 of 42 PASS not_null_int_trips_total_amount .................................. [PASS in 0.01s]
17:13:43  21 of 42 START test not_null_int_trips_trip_id ................................. [RUN]
17:13:43  21 of 42 PASS not_null_int_trips_trip_id ....................................... [PASS in 0.01s]
17:13:43  22 of 42 START test not_null_int_trips_vendor_id ............................... [RUN]
17:13:43  22 of 42 PASS not_null_int_trips_vendor_id ..................................... [PASS in 0.01s]
17:13:43  23 of 42 START sql incremental model prod.fct_trips ............................ [RUN]
17:13:43  Detected columns with numeric type and unspecified precision/scale, this can lead to unintended rounding: ['trip_distance', 'fare_amount', 'extra', 'mta_tax', 'tip_amount', 'tolls_amount', 'ehail_fee', 'improvement_surcharge', 'total_amount']`
17:13:43  23 of 42 OK created sql incremental model prod.fct_trips ....................... [OK in 0.65s]
17:13:43  24 of 42 START test accepted_values_fct_trips_service_type__Green__Yellow ...... [RUN]
17:13:44  24 of 42 PASS accepted_values_fct_trips_service_type__Green__Yellow ............ [PASS in 0.34s]
17:13:44  25 of 42 START test not_null_fct_trips_pickup_datetime ......................... [RUN]
17:13:44  25 of 42 PASS not_null_fct_trips_pickup_datetime ............................... [PASS in 0.01s]
17:13:44  26 of 42 START test not_null_fct_trips_service_type ............................ [RUN]
17:13:44  26 of 42 PASS not_null_fct_trips_service_type .................................. [PASS in 0.08s]
17:13:44  27 of 42 START test not_null_fct_trips_total_amount ............................ [RUN]
17:13:44  27 of 42 PASS not_null_fct_trips_total_amount .................................. [PASS in 0.01s]
17:13:44  28 of 42 START test not_null_fct_trips_trip_id ................................. [RUN]
17:13:44  28 of 42 PASS not_null_fct_trips_trip_id ....................................... [PASS in 0.01s]
17:13:44  29 of 42 START test not_null_fct_trips_vendor_id ............................... [RUN]
17:13:44  29 of 42 PASS not_null_fct_trips_vendor_id ..................................... [PASS in 0.01s]
17:13:44  30 of 42 START test relationships_fct_trips_dropoff_location_id__location_id__ref_dim_zones_  [RUN]
17:13:44  30 of 42 PASS relationships_fct_trips_dropoff_location_id__location_id__ref_dim_zones_  [PASS in 0.38s]
17:13:44  31 of 42 START test relationships_fct_trips_pickup_location_id__location_id__ref_dim_zones_  [RUN]
17:13:44  31 of 42 PASS relationships_fct_trips_pickup_location_id__location_id__ref_dim_zones_  [PASS in 0.27s]
17:13:44  32 of 42 START sql table model prod.dim_vendors ................................ [RUN]
17:13:44  32 of 42 OK created sql table model prod.dim_vendors ........................... [OK in 0.05s]
17:13:44  33 of 42 START sql table model prod.fct_monthly_zone_revenue ................... [RUN]
17:13:47  33 of 42 OK created sql table model prod.fct_monthly_zone_revenue .............. [OK in 3.10s]
17:13:47  34 of 42 START test not_null_dim_vendors_vendor_id ............................. [RUN]
17:13:47  34 of 42 PASS not_null_dim_vendors_vendor_id ................................... [PASS in 0.01s]
17:13:47  35 of 42 START test unique_dim_vendors_vendor_id ............................... [RUN]
17:13:47  35 of 42 PASS unique_dim_vendors_vendor_id ..................................... [PASS in 0.01s]
17:13:47  36 of 42 START test accepted_values_fct_monthly_zone_revenue_service_type__Green__Yellow  [RUN]
17:13:48  36 of 42 PASS accepted_values_fct_monthly_zone_revenue_service_type__Green__Yellow  [PASS in 0.01s]
17:13:48  37 of 42 START test dbt_utils_unique_combination_of_columns_fct_monthly_zone_revenue_pickup_zone__revenue_month__service_type  [RUN]
17:13:48  37 of 42 PASS dbt_utils_unique_combination_of_columns_fct_monthly_zone_revenue_pickup_zone__revenue_month__service_type  [PASS in 0.02s]
17:13:48  38 of 42 START test not_null_fct_monthly_zone_revenue_pickup_zone .............. [RUN]
17:13:48  38 of 42 PASS not_null_fct_monthly_zone_revenue_pickup_zone .................... [PASS in 0.01s]
17:13:48  39 of 42 START test not_null_fct_monthly_zone_revenue_revenue_month ............ [RUN]
17:13:48  39 of 42 PASS not_null_fct_monthly_zone_revenue_revenue_month .................. [PASS in 0.01s]
17:13:48  40 of 42 START test not_null_fct_monthly_zone_revenue_revenue_monthly_total_amount  [RUN]
17:13:48  40 of 42 PASS not_null_fct_monthly_zone_revenue_revenue_monthly_total_amount ... [PASS in 0.02s]
17:13:48  41 of 42 START test not_null_fct_monthly_zone_revenue_service_type ............. [RUN]
17:13:48  41 of 42 PASS not_null_fct_monthly_zone_revenue_service_type ................... [PASS in 0.01s]
17:13:48  42 of 42 START test not_null_fct_monthly_zone_revenue_total_monthly_trips ...... [RUN]
17:13:48  42 of 42 PASS not_null_fct_monthly_zone_revenue_total_monthly_trips ............ [PASS in 0.01s]
17:13:48  
17:13:48  Finished running 1 incremental model, 2 seeds, 1 snapshot, 5 table models, 31 data tests, 2 view models in 0 hours 2 minutes and 55.44 seconds (175.44s).
17:13:48  
17:13:48  Completed successfully
17:13:48  
17:13:48  Done. PASS=42 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=42
```

```text
uv run dbt run --select int_trips_unioned
17:26:55  Running with dbt=1.11.6
17:26:56  Registered adapter: duckdb=1.10.1
17:26:56  Found 8 models, 1 snapshot, 2 seeds, 31 data tests, 3 sources, 620 macros
17:26:56  
17:26:56  Concurrency: 1 threads (target='dev')
17:26:56  
17:26:56  1 of 1 START sql table model dev.int_trips_unioned ............................. [RUN]
17:26:58  1 of 1 OK created sql table model dev.int_trips_unioned ........................ [OK in 2.26s]
17:26:58  
17:26:58  Finished running 1 table model in 0 hours 0 minutes and 2.40 seconds (2.40s).
17:26:58  
17:26:58  Completed successfully
17:26:58  
17:26:58  Done. PASS=1 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=1
```

Q2

Edit file and remove values leave [1]:

04_analytics-engineering/analytics_engineering/models/marts/schema.yml

```yaml
data_tests:
    - accepted_values:
        arguments:
        values: [1, 2, 3, 4, 5]
        quote: false
```

```text
uv run dbt test --select fct_trips
17:33:11  Running with dbt=1.11.6
17:33:12  Registered adapter: duckdb=1.10.1
17:33:12  Found 8 models, 1 snapshot, 2 seeds, 32 data tests, 3 sources, 620 macros
17:33:12  
17:33:12  Concurrency: 1 threads (target='dev')
17:33:12  
17:33:12  1 of 9 START test accepted_values_fct_trips_payment_type__False__1__2__3__4 .... [RUN]
17:33:12  1 of 9 FAIL 1 accepted_values_fct_trips_payment_type__False__1__2__3__4 ........ [FAIL 1 in 0.03s]
17:33:12  2 of 9 START test accepted_values_fct_trips_service_type__Green__Yellow ........ [RUN]
17:33:12  2 of 9 PASS accepted_values_fct_trips_service_type__Green__Yellow .............. [PASS in 0.02s]
17:33:12  3 of 9 START test not_null_fct_trips_pickup_datetime ........................... [RUN]
17:33:12  3 of 9 PASS not_null_fct_trips_pickup_datetime ................................. [PASS in 0.01s]
17:33:12  4 of 9 START test not_null_fct_trips_service_type .............................. [RUN]
17:33:12  4 of 9 PASS not_null_fct_trips_service_type .................................... [PASS in 0.01s]
17:33:12  5 of 9 START test not_null_fct_trips_total_amount .............................. [RUN]
17:33:12  5 of 9 PASS not_null_fct_trips_total_amount .................................... [PASS in 0.01s]
17:33:12  6 of 9 START test not_null_fct_trips_trip_id ................................... [RUN]
17:33:12  6 of 9 PASS not_null_fct_trips_trip_id ......................................... [PASS in 0.01s]
17:33:12  7 of 9 START test not_null_fct_trips_vendor_id ................................. [RUN]
17:33:12  7 of 9 PASS not_null_fct_trips_vendor_id ....................................... [PASS in 0.01s]
17:33:12  8 of 9 START test relationships_fct_trips_dropoff_location_id__location_id__ref_dim_zones_  [RUN]
17:33:12  8 of 9 PASS relationships_fct_trips_dropoff_location_id__location_id__ref_dim_zones_  [PASS in 0.02s]
17:33:12  9 of 9 START test relationships_fct_trips_pickup_location_id__location_id__ref_dim_zones_  [RUN]
17:33:12  9 of 9 PASS relationships_fct_trips_pickup_location_id__location_id__ref_dim_zones_  [PASS in 0.02s]
17:33:12  
17:33:12  Finished running 9 data tests in 0 hours 0 minutes and 0.28 seconds (0.28s).
17:33:12  
17:33:12  Completed with 1 error, 0 partial successes, and 0 warnings:
17:33:12  
17:33:12  Failure in test accepted_values_fct_trips_payment_type__False__1__2__3__4 (models/marts/schema.yml)
17:33:12    Got 1 result, configured to fail if != 0
17:33:12  
17:33:12    compiled code at target/compiled/analytics_engineering/models/marts/schema.yml/accepted_values_fct_trips_payment_type__False__1__2__3__4.sql
17:33:12  
17:33:12  Done. PASS=8 WARN=0 ERROR=1 SKIP=0 NO-OP=0 TOTAL=9
```

Q3

```text
uv run dbt show --target prod --inline "select count(*) as record_count from {{ ref('fct_monthly_zone_revenue') }}"
17:37:55  Running with dbt=1.11.6
17:37:55  Registered adapter: duckdb=1.10.1
17:37:55  Unable to do partial parsing because config vars, config profile, or config target have changed
17:37:55  Unable to do partial parsing because profile has changed
17:37:57  Found 8 models, 1 snapshot, 2 seeds, 32 data tests, 1 sql operation, 3 sources, 620 macros
17:37:57  
17:37:57  Concurrency: 1 threads (target='prod')
17:37:57  
Previewing inline node:
| record_count |
| ------------ |
|        12184 |
```

Q4

```text
uv run dbt show --target prod --limit 5 --inline "select pickup_zone, sum(revenue_monthly_total_amount) as total_revenue from {{ ref('fct_monthly_zone_revenue') }} where service_type = 'Green' and revenue_month >= '2020-01-01' and revenue_month < '2021-01-01' group by pickup_zone order by total_revenue desc"
17:40:56  Running with dbt=1.11.6
17:40:56  Registered adapter: duckdb=1.10.1
17:40:56  Unable to do partial parsing because config vars, config profile, or config target have changed
17:40:56  Unable to do partial parsing because profile has changed
17:40:57  Found 8 models, 1 snapshot, 2 seeds, 32 data tests, 1 sql operation, 3 sources, 620 macros
17:40:57  
17:40:57  Concurrency: 1 threads (target='prod')
17:40:57  
Previewing inline node:
| pickup_zone          | total_revenue |
| -------------------- | ------------- |
| East Harlem North    |  1,817,274.15 |
| East Harlem South    |  1,653,149.51 |
| Central Harlem       |  1,097,608.82 |
| Washington Height... |    879,881.40 |
| Morningside Heights  |    764,223.04 |
```

Q5

```text
uv run dbt show --target prod --inline "select sum(total_monthly_trips) as total_trips from {{ ref('fct_monthly_zone_revenue') }} where service_type = 'Green' and revenue_month >= '2019-10-01' and revenue_month < '2019-11-01'"
17:42:10  Running with dbt=1.11.6
17:42:10  Registered adapter: duckdb=1.10.1
17:42:10  Unable to do partial parsing because config vars, config profile, or config target have changed
17:42:10  Unable to do partial parsing because profile has changed
17:42:11  Found 8 models, 1 snapshot, 2 seeds, 32 data tests, 1 sql operation, 3 sources, 620 macros
17:42:11  
17:42:11  Concurrency: 1 threads (target='prod')
17:42:11  
Previewing inline node:
| total_trips |
| ----------- |
|      384624 |
```

Q6

```text
uv run dbt show --target prod --vars '{load_fhv_data: true}' --inline "select count(*) as record_count from {{ ref('stg_fhv_tripdata') }}"
17:44:25  Running with dbt=1.11.6
17:44:26  Registered adapter: duckdb=1.10.1
17:44:26  Unable to do partial parsing because config vars, config profile, or config target have changed
17:44:26  Unable to do partial parsing because profile has changed
17:44:27  Found 9 models, 1 snapshot, 2 seeds, 34 data tests, 1 sql operation, 3 sources, 620 macros
17:44:27  
17:44:27  Concurrency: 1 threads (target='prod')
17:44:27  
Previewing inline node:
| record_count |
| ------------ |
|     43244693 |
```
