-- DQ-CRM-004 (Critical): the same organisation entered more than once.
-- Matching is on the normalised name built in staging, which strips legal
-- suffixes and punctuation. Credit exposure is calculated per client
-- record, so a split client understates the firm's true exposure.

with grouped as (
    select
        client_name_normalised,
        count(*)                      as record_count,
        min(client_id)                as retained_client_id,
        string_agg(client_id, ', ')   as all_client_ids
    from {{ ref('stg_crm_clients') }}
    where client_name_normalised is not null
      and client_name_normalised <> ''
    group by client_name_normalised
    having count(*) > 1
)

select
    client_name_normalised,
    record_count,
    retained_client_id,
    all_client_ids
from grouped