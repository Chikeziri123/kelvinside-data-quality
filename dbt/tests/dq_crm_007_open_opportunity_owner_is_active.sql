-- DQ-CRM-007 (Critical): live pipeline owned by someone who has left.
-- The opportunity stays in the forecast, nobody works it, and the loss
-- surfaces only when the expected close date passes.

select
    o.opportunity_id,
    o.client_id,
    o.stage,
    o.value_gbp,
    o.expected_close_date,
    o.owner_employee_id,
    e.employment_status,
    e.leaver_date
from {{ ref('stg_crm_opportunities') }} o
left join {{ ref('stg_hr_employees') }} e
    on o.owner_employee_id = e.employee_id
where o.is_open
  and o.owner_employee_id is not null
  and (e.employee_id is null or e.employment_status = 'Leaver')