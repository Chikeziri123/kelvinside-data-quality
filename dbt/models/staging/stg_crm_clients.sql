with source as (
    select * from {{ source('raw', 'crm_clients') }}
)

select
    client_id,
    nullif(trim(client_name), '')                       as client_name,
    -- Normalised name for duplicate detection. Only the suffixes that
    -- denote the SAME legal entity written differently are stripped:
    -- Ltd and Limited, PLC and Plc. Group, Holdings and LLC are retained
    -- because "Jones Group" and "Jones Ltd" are different companies, and
    -- collapsing them produces false positives that erode steward trust
    -- in the whole scorecard. See ADR-002.
    regexp_replace(
        lower(
            regexp_replace(
                coalesce(client_name, ''),
                '\s+(ltd|limited)\.?$',
                '',
                'gi'
            )
        ),
        '[^a-z0-9]',
        '',
        'g'
    )                                                   as client_name_normalised,
    nullif(upper(trim(postcode)), '')                   as postcode,
    nullif(trim(industry), '')                          as industry,
    nullif(trim(account_manager_employee_id), '')       as account_manager_employee_id,
    nullif(trim(status), '')                            as status,
    try_cast(nullif(created_date, '') as date)          as created_date,
    try_cast(nullif(last_updated, '') as date)          as last_updated
from source