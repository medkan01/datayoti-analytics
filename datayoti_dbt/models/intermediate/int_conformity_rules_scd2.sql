select
    dbt_scd_id as rule_sk,
    rule_id,
    site_source_id,
    metric_type,
    min_allowed,
    max_allowed,
    criticality_level,
    description,

    dbt_valid_from as valid_from_ts,
    dbt_valid_to as valid_to_ts,
    case 
        when dbt_valid_to is null then true
        else false
    end as is_current
from {{ ref('conformity_rules_snapshot') }}