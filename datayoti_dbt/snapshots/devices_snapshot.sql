{% snapshot devices_snapshot %}

{{ config(
        target_schema='snapshots',
        unique_key='device_source_id',
        strategy='timestamp',
        updated_at='updated_ts',
) }}

select
    device_source_id,
    device_mac_addr,
    site_source_id,
    created_ts,
    updated_ts
from {{ ref('int_devices') }}

{% endsnapshot %}