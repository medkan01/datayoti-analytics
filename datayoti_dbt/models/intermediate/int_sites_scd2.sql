select 
    dbt_scd_id as site_sk,
    site_source_id,
    site_ref,
    site_name,
    site_description,

    dbt_valid_from as valid_from_ts,
    dbt_valid_to as valid_to_ts,
    case 
        when dbt_valid_to is null then true
        else false
    end as is_current
from {{ ref('sites_snapshot') }}