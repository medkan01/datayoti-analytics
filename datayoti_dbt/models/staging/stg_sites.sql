select
    cast(id as integer) as site_id,
    cast(site_id as varchar(8)) as site_ref,
    cast(site_name as varchar(30)) as site_name,
    cast(description as varchar(255)) as description,
    cast(created_at as timestamp) as created_ts,
    cast(updated_at as timestamp) as updated_ts
from 
    {{ source('raw_iot', 'raw_sites') }}
where
    id is not null
    and site_id is not null