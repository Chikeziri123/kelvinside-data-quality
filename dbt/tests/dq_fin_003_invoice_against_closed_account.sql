-- DQ-FIN-003 (Critical): an invoice raised against an account Finance has
-- closed. Raised at the Operations Board as a direct cause of write-offs
-- and client relationship damage. Neither system can see this alone:
-- Finance holds the account status, and the invoice looks valid in
-- isolation.

select
    i.invoice_number,
    i.account_id,
    i.invoice_date,
    i.amount_gbp,
    i.status              as invoice_status,
    a.account_name,
    a.status              as account_status,
    a.closed_date         as account_closed_date
from {{ ref('stg_finance_invoices') }} i
join {{ ref('stg_finance_client_accounts') }} a
    on i.account_id = a.account_id
where a.status = 'Closed'