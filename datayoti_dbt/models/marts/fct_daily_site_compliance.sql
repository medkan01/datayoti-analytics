select
    dcr.rule_sk,
    dse.event_day_sk,
    dcr.metric_type,
    
    dse.min_temperature_celsius_on_site,
    dse.max_temperature_celsius_on_site,
    dse.temperature_range_on_site,

    dse.min_humidity_percentage_on_site,
    dse.max_humidity_percentage_on_site,
    dse.humidity_range_on_site,

    dse.uptime_ratio_on_site,
    dse.data_validity_on_site,
    dse.total_readings_on_site,

    case
        when dcr.metric_type = 'temperature_range' then
            case 
                when dse.min_temperature_celsius_on_site >= dcr.min_allowed 
                     and dse.max_temperature_celsius_on_site <= dcr.max_allowed then true
                else false
            end

        when dcr.metric_type = 'humidity_floor' then
            case 
                when dse.min_humidity_percentage_on_site >= dcr.min_allowed then true
                else false
            end

        when dcr.metric_type = 'humidity_ceiling' then
            case
                when dse.max_humidity_percentage_on_site <= dcr.max_allowed then true
                else false
            end

        when dcr.metric_type = 'temperature_stability' then
            case
                when dse.temperature_stability_on_site <= dcr.max_allowed then true
                else false
            end

        when dcr.metric_type = 'uptime_ratio' then
            case
                when dse.uptime_ratio_on_site >= dcr.min_allowed then true
                else false
            end

        when dcr.metric_type = 'data_validity' then
            case
                when dse.data_validity_on_site >= dcr.min_allowed then true
                else false
            end

        else null
    end as is_compliant
                
from {{ ref('int_daily_site_env') }} as dse

join {{ ref('dim_sites') }} as ds
    on dse.site_sk = ds.site_sk
    and ds.is_current = true

join {{ ref('dim_conformity_rules') }} as dcr
    on ds.site_source_id = dcr.site_source_id
    and dcr.is_current = true

