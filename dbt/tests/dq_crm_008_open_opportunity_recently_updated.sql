-- DQ-CRM-008 (Medium): an open opportunity untouched for 180 days is not
-- pipeline, it is an unclosed record. Including it inflates the forecast
-- and distorts resource planning.

select
    opportunity_id,
    client_id,
    stage,
    value_gbp,
    owner_employee_id,
    last_updated,
    date_diff('day', last_updated, date '{{ var("extract_date") }}') as days_since_update
from {{ ref('stg_crm_opportunities') }}
where is_open
  and last_updated is not null
  and last_updated < date '{{ var("extract_date") }}' - interval 180 day