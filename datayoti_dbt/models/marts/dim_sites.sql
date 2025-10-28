select
    site_sk,
    site_source_id,
    site_ref,
    site_name,
    site_description,
    valid_from_ts,
    valid_to_ts,
    is_current
from {{ ref('int_sites_scd2') }}