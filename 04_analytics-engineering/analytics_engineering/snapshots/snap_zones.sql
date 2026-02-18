{% snapshot snap_zones %}

{{
    config(
        target_schema='snapshots',
        unique_key='location_id',
        strategy='check',
        check_cols=['borough', 'zone', 'service_zone'],
    )
}}

-- SCD Type 2 snapshot: tracks changes to taxi zone definitions over time.
--
-- If a zone's borough, name, or service_zone ever changes, dbt creates a new
-- row preserving the old values with dbt_valid_from / dbt_valid_to timestamps.
-- The current record always has dbt_valid_to = NULL.
--
-- In this project the zone data is static (it comes from a seed CSV), so this
-- snapshot won't capture real changes. It exists to demonstrate the pattern.
-- In a real project, you'd snapshot a source table that gets overwritten —
-- e.g., an orders table where status changes from 'pending' to 'shipped'.
--
-- Run with: dbt snapshot

select
    locationid as location_id,
    borough,
    zone,
    service_zone
from {{ ref('taxi_zone_lookup') }}

{% endsnapshot %}
