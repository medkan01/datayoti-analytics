select
    cast(id as integer) as device_id,
    cast(device_id as varchar(17)) as mac_addr, -- Format d'adresse MAC (XX:XX:XX:XX:XX:XX)
    cast(site_id as varchar(8)) as site_ref,
    cast(created_at as timestamp) as created_ts,
    cast(updated_at as timestamp) as updated_ts
from 
    {{ source('raw_iot', 'raw_devices') }}
where
    id is not null
    and device_id is not null
    and site_id is not null