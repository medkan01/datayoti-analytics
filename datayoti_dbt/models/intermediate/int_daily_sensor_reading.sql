with joined_data as (
    select
        d.device_sk as device_sk,
        s.site_sk,
        sd.event_ts,
        sd.temperature_celsius,
        sd.humidity_percentage
    
    from {{ ref('stg_sensor_data') }} as sd

    join {{ ref('dim_devices') }} as d
        on sd.device_mac_addr = d.device_mac_addr
        and sd.event_ts >= d.valid_from_ts
        and (
            sd.event_ts < d.valid_to_ts
            or d.valid_to_ts is null
        )
    
    join {{ ref('dim_sites') }} as s
        on d.site_source_id = s.site_source_id
        and sd.event_ts >= s.valid_from_ts
        and (
            sd.event_ts < s.valid_to_ts
            or s.valid_to_ts is null
        )
) -- End of CTE


select
    jd.device_sk,
    jd.site_sk,
    date_trunc('day', jd.event_ts) as event_day_sk,

    avg(jd.temperature_celsius) as avg_temperature_celsius,
    min(jd.temperature_celsius) as min_temperature_celsius,
    max(jd.temperature_celsius) as max_temperature_celsius,

    avg(jd.humidity_percentage) as avg_humidity_percentage,
    min(jd.humidity_percentage) as min_humidity_percentage,
    max(jd.humidity_percentage) as max_humidity_percentage,

    count(*) as total_readings

from joined_data as jd

join {{ ref('dim_dates') }} as dd
    on date_trunc('day', jd.event_ts) = dd.date_day

group by
    jd.device_sk,
    jd.site_sk,
    event_day_sk