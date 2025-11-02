select
    dsr.site_sk,
    dsr.event_day_sk,

    -- Métriques de température
    AVG(dsr.min_temperature_celsius) as min_temperature_celsius_on_site,
    AVG(dsr.max_temperature_celsius) as max_temperature_celsius_on_site,
    (AVG(dsr.max_temperature_celsius) - AVG(dsr.min_temperature_celsius)) as temperature_range_on_site,
    
    -- Métriques d'humidité
    AVG(dsr.min_humidity_percentage) as min_humidity_percentage_on_site,
    AVG(dsr.max_humidity_percentage) as max_humidity_percentage_on_site,
    (AVG(dsr.max_humidity_percentage) - AVG(dsr.min_humidity_percentage)) as humidity_range_on_site,

    -- Métriques dérivées pour conformité
    ABS(AVG(dsr.max_temperature_celsius) - AVG(dsr.min_temperature_celsius)) as temperature_stability_on_site,
    
    -- Ratio de disponibilité (estimé basé sur un nombre attendu de lectures par jour)
    CASE 
        WHEN SUM(dsr.total_readings) >= 1440 THEN 1.0  -- 1440 = 24h * 60min (estimation 1 lecture/minute)
        ELSE CAST(SUM(dsr.total_readings) AS FLOAT) / 1440.0
    END as uptime_ratio_on_site,
    
    -- Validité des données (basé sur cohérence des mesures)
    CASE 
        WHEN AVG(dsr.min_temperature_celsius) > 5 
             AND AVG(dsr.min_humidity_percentage) > 10 
             AND SUM(dsr.total_readings) >= 50 
        THEN 1.0
        ELSE 0.0
    END as data_validity_on_site,

    -- Métriques de volume
    SUM(dsr.total_readings) as total_readings_on_site

from {{ ref('int_daily_sensor_reading') }} as dsr

join {{ ref('dim_sites') }} as ds
    on dsr.site_sk = ds.site_sk

group by
    dsr.site_sk,
    dsr.event_day_sk