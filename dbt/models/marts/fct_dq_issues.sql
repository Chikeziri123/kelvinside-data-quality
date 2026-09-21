{{ config(materialized='table') }}

-- Every breached rule becomes one managed issue.
--
-- The issue, not the rule failure, is the unit of work. It carries an
-- owner, a steward, an SLA target date and a status. Without this layer
-- the platform reports problems and stops, which is the failure mode of
-- most data quality tooling: the dashboard goes red and nobody is
-- accountable for making it green.

with breached as (
    select *
    from {{ ref('fct_rule_results') }}
    where is_breached
),

issues as (
    select
        -- Deterministic issue key: the same breach on the same run date
        -- always produces the same issue, so re-running the pipeline does
        -- not duplicate the backlog.
        'ISS-' || replace(rule_id, 'DQ-', '') || '-'
            || strftime(run_date, '%Y%m%d')  as issue_id,
        run_date                             as raised_date,
        rule_id,
        source_system,
        subject_table,
        dimension,
        severity,
        rule_description,
        owner_role,
        steward_role,
        failing_records,
        failure_rate_pct,
        threshold_pct,
        sla_days,
        run_date + sla_days                  as sla_due_date,
        -- Root cause is assigned from the quality dimension as a first
        -- pass. The steward overwrites it on investigation, which is why
        -- the provisional value is labelled as such rather than presented
        -- as fact.
        case dimension
            when 'Completeness' then 'Provisional: capture gap at point of entry'
            when 'Validity' then 'Provisional: absent or unenforced input validation'
            when 'Uniqueness' then 'Provisional: no duplicate check at creation'
            when 'Referential integrity' then 'Provisional: no cross-system key enforcement'
            when 'Consistency' then 'Provisional: status change not propagated between systems'
            when 'Timeliness' then 'Provisional: no review cadence for ageing records'
        end                                  as provisional_root_cause,
        'Open'                               as issue_status,
        cast(null as date)                   as resolved_date
    from breached
)

select
    issue_id,
    raised_date,
    sla_due_date,
    date_diff('day', raised_date, sla_due_date) as sla_days_allowed,
    date_diff('day', date '{{ var("extract_date") }}', sla_due_date) as days_remaining,
    case
        when issue_status = 'Resolved' then 'Resolved'
        when sla_due_date < date '{{ var("extract_date") }}' then 'Overdue'
        when date_diff('day', date '{{ var("extract_date") }}', sla_due_date) <= 1 then 'Due now'
        else 'On track'
    end                                         as sla_status,
    -- Escalation follows the catalogue: an overdue issue leaves the
    -- steward and lands with the accountable owner.
    case
        when sla_due_date < date '{{ var("extract_date") }}' then owner_role
        else steward_role
    end                                         as currently_assigned_to,
    rule_id,
    source_system,
    subject_table,
    dimension,
    severity,
    rule_description,
    owner_role,
    steward_role,
    failing_records,
    failure_rate_pct,
    threshold_pct,
    provisional_root_cause,
    issue_status,
    resolved_date
from issues