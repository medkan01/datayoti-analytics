select
    d.device_id,
    date_trunc('hour', sd.event_ts) as event_hour_ts,

    avg(sd.rssi_dbm) as avg_rssi_dbm,
    min(sd.rssi_dbm) as min_rssi_dbm,
    max(sd.rssi_dbm) as max_rssi_dbm,

    avg(sd.free_heap_bytes) as avg_free_heap_bytes,
    min(sd.free_heap_bytes) as min_free_heap_bytes,
    max(sd.free_heap_bytes) as max_free_heap_bytes,

    avg(sd.min_heap_bytes) as avg_min_heap_bytes,
    min(sd.min_heap_bytes) as min_min_heap_bytes,
    max(sd.min_heap_bytes) as max_min_heap_bytes,

    avg(sd.uptime_secs) as avg_uptime_secs,
    min(sd.uptime_secs) as min_uptime_secs,
    max(sd.uptime_secs) as max_uptime_secs,

    min(date_trunc('hour', sd.reception_ts)) as first_reception_hour_ts,
    max(date_trunc('hour', sd.reception_ts)) as last_reception_hour_ts
from 
    {{ ref('stg_device_heartbeats') }} as sd
join 
    {{ ref('stg_devices') }} as d 
    on sd.device_mac_addr = d.mac_addr
where
    d.device_id is not null
    and d.mac_addr is not null
    and sd.device_mac_addr is not null
group by
    d.device_id,
    event_hour_ts