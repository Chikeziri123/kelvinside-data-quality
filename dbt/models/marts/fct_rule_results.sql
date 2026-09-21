{{ config(materialized='table') }}

-- One row per rule per run: failure count, rate against the population
-- the rule actually examines, and the verdict against the catalogue
-- threshold.
--
-- Rate is calculated on population_in_scope, not the full table. A rule
-- cannot fail a row it never looked at, and measuring against the whole
-- table understates the rate for every filtered rule. See ADR-003.
--
-- Verdict is separate from the dbt test outcome. dbt reports any failing
-- row as a warning, but the business accepts up to five percent on a Low
-- severity rule. The threshold decides breach, not the presence of
-- failures.

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
        res.population_filter_applied,
        res.failing_records,
        res.population_in_scope,
        res.population_total,
        case
            when res.population_in_scope = 0 then 0
            else round(100.0 * res.failing_records / res.population_in_scope, 4)
        end as failure_rate_pct,
        case
            when res.population_total = 0 then 0
            else round(100.0 * res.population_in_scope / res.population_total, 2)
        end as scope_coverage_pct
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
    population_filter_applied,
    failing_records,
    population_in_scope,
    population_total,
    scope_coverage_pct,
    failure_rate_pct,
    failure_rate_pct > threshold_pct  as is_breached,
    case
        when failing_records = 0 then 'Clean'
        when failure_rate_pct > threshold_pct then 'Breached'
        else 'Within tolerance'
    end                               as rule_status,
    round(100.0 - failure_rate_pct, 4) as pass_rate_pct
from joined