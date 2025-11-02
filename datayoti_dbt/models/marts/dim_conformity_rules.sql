select
    rule_sk,
    rule_id,
    site_source_id,
    metric_type,
    min_allowed,
    max_allowed,
    criticality_level,
    description,
    valid_from_ts,
    valid_to_ts,
    is_current
from {{ ref('int_conformity_rules_scd2') }}
