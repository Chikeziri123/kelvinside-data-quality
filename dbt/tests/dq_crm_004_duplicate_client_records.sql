-- DQ-CRM-004 (Critical): the same organisation entered more than once.
--
-- Matching requires BOTH a normalised name match AND an identical
-- postcode. Name alone produced false positives at a rate that would
-- have made the finding unactionable: common surnames recur across
-- unrelated clients, so "Jones PLC" and "Jones Group" collapsed together
-- despite being separate legal entities.
--
-- Credit exposure is calculated per client record, so a split client
-- understates the firm's true exposure to that organisation.

with candidates as (
    select
        client_id,
        client_name,
        client_name_normalised,
        postcode
    from {{ ref('stg_crm_clients') }}
    where client_name_normalised is not null
      and client_name_normalised <> ''
      and postcode is not null
),

grouped as (
    select
        client_name_normalised,
        postcode,
        count(*)                        as record_count,
        min(client_id)                  as retained_client_id,
        string_agg(client_id, ', ')     as all_client_ids,
        string_agg(client_name, ' / ')  as all_client_names
    from candidates
    group by client_name_normalised, postcode
    having count(*) > 1
)

select
    client_name_normalised,
    postcode,
    record_count,
    retained_client_id,
    all_client_ids,
    all_client_names
from grouped