-- DQ-FIN-005 (Critical): revenue posted to a cost centre closed during
-- the reorganisation. Practice profitability is understated where the
-- revenue should have landed and the closed centre carries income nobody
-- reviews. Escalates to the Finance Director because cost centre is
-- shared data between Finance and HR.

select
    i.invoice_number,
    i.account_id,
    i.invoice_date,
    i.amount_gbp,
    i.cost_centre_code,
    cc.cost_centre_name,
    cc.status        as cost_centre_status,
    cc.closed_date   as cost_centre_closed_date
from {{ ref('stg_finance_invoices') }} i
join {{ ref('stg_finance_cost_centres') }} cc
    on i.cost_centre_code = cc.cost_centre_code
where cc.status = 'Closed'