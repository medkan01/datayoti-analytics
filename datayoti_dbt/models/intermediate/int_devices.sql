select
    d.device_source_id,
    d.device_mac_addr,
    s.site_source_id,
    d.created_ts as created_ts,
    d.updated_ts as updated_ts
from {{ ref('stg_devices') }} as d
left join {{ ref('stg_sites') }} as s
    on d.site_ref = s.site_ref
where d.site_ref is not null
