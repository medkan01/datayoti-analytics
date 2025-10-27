select
    cast(time as timestamp) as event_ts,
    cast(device_id as varchar(17)) as device_mac_addr, -- Format d'adresse MAC (XX:XX:XX:XX:XX:XX)
    cast(temperature as float) as temperature_celsius,
    cast(humidity as float) as humidity_percentage,
    cast(reception_time as timestamp) as reception_ts
from
    {{ source('raw_iot', 'raw_sensor_data') }}
where
    time is not null
    and device_id is not null
    and temperature is not null
    and humidity is not null