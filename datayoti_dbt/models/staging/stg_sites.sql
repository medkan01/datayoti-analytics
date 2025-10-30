select
    cast(id as integer) as site_source_id,
    cast(site_ref as varchar(8)) as site_ref,
    cast(site_name as varchar(30)) as site_name,
    cast(description as varchar(255)) as site_description,
    cast(created_at as timestamp) as created_ts,
    cast(updated_at as timestamp) as updated_ts
from {{ source('raw_iot', 'raw_sites') }}
where id is not null
and site_ref is not null
and created_at is not null