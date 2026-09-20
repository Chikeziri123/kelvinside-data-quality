with source as (
    select * from {{ source('raw', 'finance_suppliers') }}
)

select
    supplier_id,
    nullif(trim(supplier_name), '')                         as supplier_name,
    nullif(trim(vat_number), '')                            as vat_number,
    try_cast(nullif(payment_terms_days, '') as integer)     as payment_terms_days,
    nullif(trim(status), '')                                as status
from source