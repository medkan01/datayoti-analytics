{{ config(materialized='table', schema='raw') }}

select
    cast(null as text) as id,
    cast(null as text) as site_ref,
    cast(null as text) as site_name,
    cast(null as text) as description,
    cast(null as text) as created_at,
    cast(null as text) as updated_at
where false