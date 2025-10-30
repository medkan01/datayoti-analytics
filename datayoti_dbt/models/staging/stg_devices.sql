select
    cast(id as integer) as device_source_id,
    cast(device_mac_addr as varchar(17)) as device_mac_addr, -- Format d'adresse MAC (XX:XX:XX:XX:XX:XX)
    cast(site_ref as varchar(8)) as site_ref,
    cast(created_at as timestamp) as created_ts,
    cast(updated_at as timestamp) as updated_ts
from {{ source('raw_iot', 'raw_devices') }}
where id is not null
and device_mac_addr is not null
and site_ref is not null