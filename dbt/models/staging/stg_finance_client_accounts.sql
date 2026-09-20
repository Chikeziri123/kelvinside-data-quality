with source as (
    select * from {{ source('raw', 'finance_client_accounts') }}
)

select
    account_id,
    nullif(trim(crm_client_ref), '')                        as crm_client_ref,
    nullif(trim(account_name), '')                          as account_name,
    nullif(trim(status), '')                                as status,
    status = 'Open'                                         as is_open,
    try_cast(nullif(credit_limit_gbp, '') as decimal(18, 2)) as credit_limit_gbp,
    try_cast(nullif(opened_date, '') as date)               as opened_date,
    try_cast(nullif(closed_date, '') as date)               as closed_date
from source