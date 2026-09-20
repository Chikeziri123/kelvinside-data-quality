with source as (
    select * from {{ source('raw', 'crm_clients') }}
)

select
    client_id,
    nullif(trim(client_name), '')                       as client_name,
    -- Normalised name supports duplicate detection without altering the
    -- record the business sees. Legal suffixes and punctuation are the
    -- main cause of the same organisation being entered twice.
    regexp_replace(
        lower(
            regexp_replace(
                coalesce(client_name, ''),
                '\s+(ltd|limited|plc|llp|group|holdings)\.?$',
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