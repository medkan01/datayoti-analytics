select
    dbt_scd_id as device_sk,
    device_source_id,
    device_mac_addr,
    site_source_id,
    
    dbt_valid_from as valid_from_ts,
    dbt_valid_to as valid_to_ts,
    case 
        when dbt_valid_to is null then true
        else false
    end as is_current
from {{ ref('devices_snapshot') }}