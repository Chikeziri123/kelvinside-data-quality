-- DQ-CRM-003 (High): the named account manager must still work here.
-- A client owned by a leaver has nobody accountable for the relationship,
-- and the gap is invisible in CRM because the field is populated.

select
    c.client_id,
    c.client_name,
    c.account_manager_employee_id,
    e.employment_status,
    e.leaver_date
from {{ ref('stg_crm_clients') }} c
left join {{ ref('stg_hr_employees') }} e
    on c.account_manager_employee_id = e.employee_id
where c.status = 'Active'
  and c.account_manager_employee_id is not null
  and (e.employee_id is null or e.employment_status = 'Leaver')