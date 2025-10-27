{{ config(materialized='table', schema='raw') }}

select
    cast(null as text) as time,
    cast(null as text) as device_id,
    cast(null as text) as site_id,
    cast(null as text) as rssi,
    cast(null as text) as free_heap,
    cast(null as text) as uptime,
    cast(null as text) as min_heap,
    cast(null as text) as ntp_sync,
    cast(null as text) as reception_time
where false