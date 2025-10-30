select
    cast(time as timestamp) as event_ts,
    cast(device_mac_addr as varchar(17)) as device_mac_addr, -- Format d'adresse MAC (XX:XX:XX:XX:XX:XX)
    cast(rssi as integer) as rssi_dbm,
    cast(free_heap as integer) as free_heap_bytes,
    cast(uptime as integer) as uptime_secs,
    cast(min_heap as integer) as min_heap_bytes,
    cast(ntp_sync as boolean) as ntp_sync,
    cast(reception_time as timestamp) as reception_ts
from 
    {{ source('raw_iot', 'raw_device_heartbeats') }}
where
    device_mac_addr is not null
    and time is not null
