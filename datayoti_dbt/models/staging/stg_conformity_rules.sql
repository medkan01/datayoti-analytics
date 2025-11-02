select
    cast(id as integer) as rule_id,
    cast(site_ref as text) as site_ref,
    cast(metric_type as text) as metric_type,
    cast(min_allowed as numeric) as min_allowed,
    cast(max_allowed as numeric) as max_allowed,
    cast(criticality as text) as criticality_level,
    cast(description as text) as description,
    cast(created_at as timestamp) as created_ts,
    cast(updated_at as timestamp) as updated_ts
from {{ ref('conformity_rules') }}