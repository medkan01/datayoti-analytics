{{ config(
    materialized='view',
    schema='marts'
) }}

select
    ds.site_sk,
    dsc.event_day_sk,

    round(cast(avg(case when dsc.is_compliant then 1.0 else 0.0 end) as numeric), 2) as compliance_rate,
    sum(case when not dsc.is_compliant and cr.criticality_level = 'HIGH' then 1 else 0 end) as nb_critical_violations,
    count(*) as total_metrics_evaluated

from {{ ref('fct_daily_site_compliance') }} as dsc

join {{ ref('dim_conformity_rules') }} as cr
    on dsc.rule_sk = cr.rule_sk
    and cr.is_current = true

join {{ ref('dim_sites') }} as ds
    on cr.site_source_id = ds.site_source_id
    and ds.is_current = true

group by
    ds.site_sk,
    dsc.event_day_sk