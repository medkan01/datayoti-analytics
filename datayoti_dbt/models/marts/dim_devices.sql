select
    device_sk,
    device_source_id,
    device_mac_addr,
    site_source_id,
    valid_from_ts,
    valid_to_ts,
    is_current
from {{ ref('int_devices_scd2') }}