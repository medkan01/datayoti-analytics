{% snapshot sites_snapshot %}

{{ config(
        target_schema='snapshots',
        unique_key='site_source_id',
        strategy='timestamp',
        updated_at='updated_ts',
) }}

select
    site_source_id,
    site_ref,
    site_name,
    site_description,
    created_ts,
    updated_ts
from {{ ref('stg_sites') }}

{% endsnapshot %}