with joined_data as (
    select
        d.device_sk as device_sk,
        s.site_sk,
        sh.event_ts,
        sh.rssi_dbm,
        sh.free_heap_bytes,
        sh.min_heap_bytes,
        sh.uptime_secs,
        sh.ntp_sync
    
    from {{ ref('stg_device_heartbeats') }} as sh

    join {{ ref('dim_devices') }} as d
        on sh.device_mac_addr = d.device_mac_addr
        and sh.event_ts >= d.valid_from_ts
        and (
            sh.event_ts < d.valid_to_ts
            or d.valid_to_ts is null
        )
    
    join {{ ref('dim_sites') }} as s
        on d.site_source_id = s.site_source_id
        and sh.event_ts >= s.valid_from_ts
        and (
            sh.event_ts < s.valid_to_ts
            or s.valid_to_ts is null
        )
) -- End of CTE

select
    jd.device_sk,
    jd.site_sk,
    date_trunc('day', jd.event_ts) as event_day_ts,

    avg(jd.rssi_dbm) as avg_rssi_dbm,
    min(jd.rssi_dbm) as min_rssi_dbm,
    max(jd.rssi_dbm) as max_rssi_dbm,

    avg(jd.free_heap_bytes) as avg_free_heap_bytes,
    min(jd.free_heap_bytes) as min_free_heap_bytes,
    max(jd.free_heap_bytes) as max_free_heap_bytes,

    avg(jd.min_heap_bytes) as avg_min_heap_bytes,
    min(jd.min_heap_bytes) as min_min_heap_bytes,
    max(jd.min_heap_bytes) as max_min_heap_bytes,

    avg(jd.uptime_secs) as avg_uptime_secs,
    min(jd.uptime_secs) as min_uptime_secs,
    max(jd.uptime_secs) as max_uptime_secs,

    sum(case when jd.ntp_sync then 1 else 0 end) as ntp_sync_count,
    count(*) as total_heartbeats

from joined_data as jd

group by
    jd.device_sk,
    jd.site_sk,
    date_trunc('day', jd.event_ts)