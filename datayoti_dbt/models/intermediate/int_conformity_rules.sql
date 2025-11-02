select
    cr.rule_id,
    s.site_source_id,
    cr.metric_type,
    cr.min_allowed,
    cr.max_allowed,
    cr.criticality_level,
    cr.description,
    cr.created_ts,
    cr.updated_ts

from {{ ref('stg_conformity_rules') }} as cr
join {{ ref('dim_sites') }} as s
    on cr.site_ref = s.site_ref
where cr.rule_id is not null
and s.site_ref is not null
and s.site_source_id is not null