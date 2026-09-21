{{ config(materialized='table') }}

-- One row per rule per run: the failure count, the rate, and the verdict
-- against the threshold declared in the catalogue.
--
-- Verdict is deliberately separate from the test outcome. dbt reports any
-- failing row as a warning, but the business decided that a Low severity
-- rule may carry up to five percent failures before it is worth anyone's
-- time. The threshold, not the presence of failures, decides whether the
-- rule is breached.

with results as (
    {{ rule_result_union() }}
),

rules as (
    select * from {{ ref('dq_rules') }}
),

joined as (
    select
        r.rule_id,
        r.source_system,
        r.table_name          as subject_table,
        r.dimension,
        r.severity,
        r.threshold_pct,
        r.owner_role,
        r.steward_role,
        r.sla_days,
        r.rule_description,
        res.failure_table,
        res.failing_records,
        res.population_records,
        case
            when res.population_records = 0 then 0
            else round(100.0 * res.failing_records / res.population_records, 4)
        end as failure_rate_pct
    from rules r
    join results res on r.rule_id = res.rule_id
)

select
    date '{{ var("extract_date") }}'  as run_date,
    rule_id,
    source_system,
    subject_table,
    dimension,
    severity,
    rule_description,
    owner_role,
    steward_role,
    sla_days,
    threshold_pct,
    failing_records,
    population_records,
    failure_rate_pct,
    failure_rate_pct > threshold_pct  as is_breached,
    case
        when failing_records = 0 then 'Clean'
        when failure_rate_pct > threshold_pct then 'Breached'
        else 'Within tolerance'
    end                               as rule_status,
    -- Pass rate is the score the domain is measured on. A rule with
    -- failures below threshold still scores at its actual rate, because
    -- reporting it as one hundred percent would hide real drift.
    round(100.0 - failure_rate_pct, 4) as pass_rate_pct
from joined