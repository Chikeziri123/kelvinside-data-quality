with source as (
    select * from {{ source('raw', 'crm_contacts') }}
)

select
    contact_id,
    nullif(trim(client_id), '')                 as client_id,
    first_name,
    last_name,
    nullif(trim(email), '')                     as email,
    nullif(trim(phone), '')                     as phone,
    nullif(trim(is_primary), '')                as is_primary,
    try_cast(nullif(last_updated, '') as date)  as last_updated
from source