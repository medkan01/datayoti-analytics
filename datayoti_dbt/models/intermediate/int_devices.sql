select
    d.device_id as device_source_id,
    d.mac_addr,
    s.site_id as site_source_id,
    d.created_ts as first_seen_ts,
    d.updated_ts as last_seen_ts
from
    {{ ref('stg_devices') }} as d
join
    {{ ref('stg_sites') }} as s
    on d.site_ref = s.site_ref
where
    s.site_id is not null
    and s.site_ref is not null
    and d.site_ref is not null
    