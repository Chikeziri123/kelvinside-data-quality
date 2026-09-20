with source as (
    select * from {{ source('raw', 'crm_opportunities') }}
)

select
    opportunity_id,
    nullif(trim(client_id), '')                          as client_id,
    nullif(trim(opportunity_name), '')                   as opportunity_name,
    nullif(trim(stage), '')                              as stage,
    stage in ('Qualify', 'Proposal', 'Negotiation')      as is_open,
    try_cast(nullif(value_gbp, '') as decimal(18, 2))    as value_gbp,
    try_cast(nullif(expected_close_date, '') as date)    as expected_close_date,
    nullif(trim(owner_employee_id), '')                  as owner_employee_id,
    try_cast(nullif(created_date, '') as date)           as created_date,
    try_cast(nullif(last_updated, '') as date)           as last_updated
from source