with source as (
    select * from {{ source('raw', 'hr_employees') }}
)

select
    employee_id,
    first_name,
    last_name,
    nullif(trim(work_email), '')                as work_email,
    nullif(trim(job_title), '')                 as job_title,
    nullif(trim(office), '')                    as office,
    nullif(trim(cost_centre_code), '')          as cost_centre_code,
    try_cast(nullif(start_date, '') as date)    as start_date,
    try_cast(nullif(leaver_date, '') as date)   as leaver_date,
    nullif(trim(employment_status), '')         as employment_status,
    try_cast(nullif(last_updated, '') as date)  as last_updated
from source