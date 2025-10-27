{{ config(materialized='table', schema='raw') }}

select
    cast(null as text) as id,
    cast(null as text) as device_id,
    cast(null as text) as site_id,
    cast(null as text) as created_at,
    cast(null as text) as updated_at
where false