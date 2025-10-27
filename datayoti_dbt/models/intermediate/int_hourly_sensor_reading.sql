select
    d.device_id,
    date_trunc('hour', sd.event_ts) as event_hour_ts,

    avg(sd.temperature_celsius) as avg_temperature_celsius,
    min(sd.temperature_celsius) as min_temperature_celsius,
    max(sd.temperature_celsius) as max_temperature_celsius,
    
    avg(sd.humidity_percentage) as avg_humidity_percentage,
    min(sd.humidity_percentage) as min_humidity_percentage,
    max(sd.humidity_percentage) as max_humidity_percentage,

    -- Metrique de qualité d'ingestion (ne sera pas utilisée dans les analyses pour l'instant)
    min(date_trunc('hour', sd.reception_ts)) as first_reception_hour_ts,
    max(date_trunc('hour', sd.reception_ts)) as last_reception_hour_ts
from 
    {{ ref('stg_sensor_data') }} as sd
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