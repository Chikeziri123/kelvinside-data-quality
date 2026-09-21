{#
    Builds a union over the stored failure tables produced by dbt test.

    Each rule writes its failing rows to main_dq_failures.<rule_name>.
    Rather than hand-maintaining a union that drifts every time a rule is
    added, the list is declared once here and the SQL is generated.

    Row counts are read from the failure tables, and the denominator comes
    from the staging model the rule runs against, so the failure rate is a
    proportion of the population the rule actually examined.
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

{% for rule_id, table_name, population_model in rules %}
select
    '{{ rule_id }}'       as rule_id,
    '{{ table_name }}'    as failure_table,
    (select count(*) from {{ target.schema }}_dq_failures.{{ table_name }}) as failing_records,
    (select count(*) from {{ ref(population_model) }})                      as population_records
{% if not loop.last %}union all{% endif %}
{% endfor %}

{% endmacro %}