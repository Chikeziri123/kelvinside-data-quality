with source as (
    select * from {{ source('raw', 'finance_invoices') }}
)

select
    invoice_number,
    nullif(trim(account_id), '')                        as account_id,
    try_cast(nullif(invoice_date, '') as date)          as invoice_date,
    try_cast(nullif(due_date, '') as date)              as due_date,
    try_cast(nullif(amount_gbp, '') as decimal(18, 2))  as amount_gbp,
    nullif(trim(status), '')                            as status,
    nullif(trim(cost_centre_code), '')                  as cost_centre_code,
    try_cast(nullif(last_updated, '') as date)          as last_updated
from source