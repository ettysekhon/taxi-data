-- Alternative: dbt_utils.union_relations can auto-union models with different schemas,
-- but it fills missing columns with NULL rather than business-logic defaults.
-- We need trip_type=1 and ehail_fee=0 for yellow, so we handle this manually.
-- See: https://github.com/dbt-labs/dbt-utils#union_relations

with green_trips as (
    select
        vendor_id,
        rate_code_id,
        pickup_location_id,
        dropoff_location_id,
        pickup_datetime,
        dropoff_datetime,
        store_and_fwd_flag,
        passenger_count,
        trip_distance,
        trip_type,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        ehail_fee,
        improvement_surcharge,
        total_amount,
        payment_type,
        'Green' as service_type
    from {{ ref('stg_green_tripdata') }}
),

yellow_trips as (
    select
        vendor_id,
        rate_code_id,
        pickup_location_id,
        dropoff_location_id,
        pickup_datetime,
        dropoff_datetime,
        store_and_fwd_flag,
        passenger_count,
        trip_distance,
        cast(1 as integer) as trip_type,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        cast(0 as numeric) as ehail_fee,
        improvement_surcharge,
        total_amount,
        payment_type,
        'Yellow' as service_type
    from {{ ref('stg_yellow_tripdata') }}
)

select * from green_trips
union all
select * from yellow_trips
