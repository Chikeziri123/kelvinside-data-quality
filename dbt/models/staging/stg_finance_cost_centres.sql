with source as (
    select * from {{ source('raw', 'finance_cost_centres') }}
)

select
    cost_centre_code,
    nullif(trim(cost_centre_name), '')          as cost_centre_name,
    nullif(trim(practice), '')                  as practice,
    nullif(trim(office), '')                    as office,
    nullif(trim(status), '')                    as status,
    status = 'Open'                             as is_open,
    try_cast(nullif(opened_date, '') as date)   as opened_date,
    try_cast(nullif(closed_date, '') as date)   as closed_date
from source