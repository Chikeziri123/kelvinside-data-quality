{{ config(materialized='table') }}

-- Ownership dimension for the scorecard's owner view. Derived from the
-- catalogue rather than maintained separately, so ownership cannot drift
-- between the governing document and the reporting layer.

with roles as (
    select distinct owner_role as role_name, 'Accountable owner' as role_type
    from {{ ref('dq_rules') }}

    union

    select distinct steward_role as role_name, 'Operational steward' as role_type
    from {{ ref('dq_rules') }}
),

rule_counts as (
    select owner_role as role_name, count(*) as rules_owned
    from {{ ref('dq_rules') }}
    group by owner_role
)

select
    r.role_name,
    r.role_type,
    coalesce(rc.rules_owned, 0) as rules_accountable_for,
    case r.role_name
        when 'Finance Director' then 'Finance'
        when 'Commercial Director' then 'Commercial'
        when 'HR Director' then 'People'
        when 'Accounts Payable Lead' then 'Finance'
        when 'Management Accountant' then 'Finance'
        when 'CRM Administrator' then 'Commercial'
        when 'HR Systems Officer' then 'People'
    end as business_function
from roles r
left join rule_counts rc on r.role_name = rc.role_name