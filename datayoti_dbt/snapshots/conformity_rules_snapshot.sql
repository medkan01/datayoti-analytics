{% snapshot conformity_rules_snapshot %}

{{ config(
        target_schema='snapshots',
        unique_key='rule_id',
        strategy='timestamp',
        updated_at='updated_ts',
) }}

select
    rule_id,
    site_source_id,
    metric_type,
    min_allowed,
    max_allowed,
    criticality_level,
    description,
    created_ts,
    updated_ts
from {{ ref('int_conformity_rules') }}

{% endsnapshot %}