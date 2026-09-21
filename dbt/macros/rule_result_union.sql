{#
    Builds a union over the stored failure tables produced by dbt test.

    Two denominators are produced for every rule:

      population_in_scope  - rows the rule actually examines, after its
                             declared filter is applied
      population_total     - every row in the subject table

    The in-scope figure is the one the failure rate and the threshold
    verdict use, because a rule cannot fail a row it never looked at.
    DQ-CRM-008 examines open opportunities only, so measuring it against
    all 900 opportunities understated its rate by a third and could let a
    breached rule report as within tolerance.

    The total is retained so the scorecard can show coverage: what
    proportion of each table any rule is watching at all.

    The population filter is declared in the rules catalogue seed, not
    here, so the filter travels with the rule definition it belongs to.
#}

{% macro rule_result_union() %}

{% set rules = [
    ('DQ-HR-001', 'dq_hr_001_active_employee_has_work_email', 'stg_hr_employees'),
    ('DQ-HR-002', 'dq_hr_002_work_email_format_valid', 'stg_hr_employees'),
    ('DQ-HR-003', 'dq_hr_003_employee_cost_centre_exists', 'stg_hr_employees'),
    ('DQ-HR-004', 'dq_hr_004_employee_has_start_date', 'stg_hr_employees'),
    ('DQ-HR-005', 'dq_hr_005_start_date_not_in_future', 'stg_hr_employees'),
    ('DQ-HR-006', 'dq_hr_006_leaver_date_after_start_date', 'stg_hr_employees'),
    ('DQ-HR-007', 'dq_hr_007_leaver_not_marked_active', 'stg_hr_employees'),
    ('DQ-CRM-001', 'dq_crm_001_postcode_format_valid', 'stg_crm_clients'),
    ('DQ-CRM-002', 'dq_crm_002_active_client_has_account_manager', 'stg_crm_clients'),
    ('DQ-CRM-003', 'dq_crm_003_client_account_manager_is_active', 'stg_crm_clients'),
    ('DQ-CRM-004', 'dq_crm_004_duplicate_client_records', 'stg_crm_clients'),
    ('DQ-CRM-005', 'dq_crm_005_contact_has_email', 'stg_crm_contacts'),
    ('DQ-CRM-006', 'dq_crm_006_contact_client_exists', 'stg_crm_contacts'),
    ('DQ-CRM-007', 'dq_crm_007_open_opportunity_owner_is_active', 'stg_crm_opportunities'),
    ('DQ-CRM-008', 'dq_crm_008_open_opportunity_recently_updated', 'stg_crm_opportunities'),
    ('DQ-CRM-009', 'dq_crm_009_opportunity_client_exists', 'stg_crm_opportunities'),
    ('DQ-CRM-010', 'dq_crm_010_opportunity_value_positive', 'stg_crm_opportunities'),
    ('DQ-FIN-001', 'dq_fin_001_account_crm_client_exists', 'stg_finance_client_accounts'),
    ('DQ-FIN-002', 'dq_fin_002_active_supplier_has_vat_number', 'stg_finance_suppliers'),
    ('DQ-FIN-003', 'dq_fin_003_invoice_against_closed_account', 'stg_finance_invoices'),
    ('DQ-FIN-004', 'dq_fin_004_invoice_account_exists', 'stg_finance_invoices'),
    ('DQ-FIN-005', 'dq_fin_005_invoice_to_closed_cost_centre', 'stg_finance_invoices'),
    ('DQ-FIN-006', 'dq_fin_006_invoice_amount_positive', 'stg_finance_invoices'),
    ('DQ-FIN-007', 'dq_fin_007_due_date_after_invoice_date', 'stg_finance_invoices'),
    ('DQ-FIN-008', 'dq_fin_008_invoice_number_unique', 'stg_finance_invoices'),
    ('DQ-FIN-009', 'dq_fin_009_credit_limit_within_approved_range', 'stg_finance_client_accounts')
] %}

{# Read the declared population filters out of the seed at compile time. #}
{% set filter_lookup = {} %}
{% if execute %}
    {% set filter_query %}
        select rule_id, population_filter from {{ ref('dq_rules') }}
    {% endset %}
    {% set filter_rows = run_query(filter_query) %}
    {% for row in filter_rows.rows %}
        {% do filter_lookup.update({row[0]: row[1]}) %}
    {% endfor %}
{% endif %}

{% for rule_id, table_name, population_model in rules %}
{% set scope_filter = filter_lookup.get(rule_id, '1=1') %}
select
    '{{ rule_id }}'    as rule_id,
    '{{ table_name }}' as failure_table,
    '{{ scope_filter | replace("'", "''") }}' as population_filter_applied,
    (select count(*) from {{ target.schema }}_dq_failures.{{ table_name }}) as failing_records,
    (select count(*) from {{ ref(population_model) }} where {{ scope_filter }}) as population_in_scope,
    (select count(*) from {{ ref(population_model) }}) as population_total
{% if not loop.last %}union all{% endif %}
{% endfor %}

{% endmacro %}