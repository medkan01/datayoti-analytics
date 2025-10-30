{{ config(materialized='table', schema='raw') }}

select
    cast(null as text) as time,
    cast(null as text) as device_mac_addr,
    cast(null as text) as temperature,
    cast(null as text) as humidity,
    cast(null as text) as reception_time
where false