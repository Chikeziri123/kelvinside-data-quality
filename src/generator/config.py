"""
Generation parameters for the Kelvinside synthetic landscape.

Every volume and defect rate is declared here rather than buried in the
generators, so a reviewer can see the shape of the data and the scale of
the injected problems in one place, and so runs are reproducible.
"""

from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Fixed seed so every run of the generator produces identical output.
# Reproducibility matters: the detection rate reported in the evidence
# pack must be verifiable by anyone who clones this repository.
SEED = 20260921

# The notional date the nightly extracts were taken.
EXTRACT_DATE = date(2026, 9, 20)

VOLUMES = {
    "cost_centres": 24,
    "employees": 400,
    "clients": 600,
    "contacts": 1500,
    "opportunities": 900,
    "suppliers": 180,
    "invoices": 2400,
}

# Defect rates are expressed as a proportion of the relevant population.
# They are deliberately higher than a mature organisation would tolerate,
# because the platform has to have something to find on day one.
DEFECT_RATES = {
    # Brackenhill HR
    "hr_missing_email": 0.03,
    "hr_invalid_email": 0.02,
    "hr_orphan_cost_centre": 0.04,
    "hr_missing_start_date": 0.01,
    "hr_future_start_date": 0.01,
    # Halstead CRM
    "crm_duplicate_client": 0.03,
    "crm_invalid_postcode": 0.03,
    "crm_missing_account_manager": 0.02,
    "crm_leaver_account_manager": 0.04,
    "crm_missing_contact_email": 0.04,
    "crm_contact_orphan_client": 0.02,
    "crm_leaver_owner": 0.05,
    "crm_stale_open_opportunity": 0.06,
    "crm_opportunity_orphan_client": 0.02,
    # Trentmoor Finance
    "fin_account_orphan_client": 0.03,
    "fin_invoice_closed_account": 0.04,
    "fin_invoice_orphan_account": 0.02,
    "fin_invoice_dead_cost_centre": 0.03,
    "fin_negative_amount": 0.015,
    "fin_duplicate_invoice_number": 0.01,
    "fin_due_before_invoice_date": 0.01,
    "fin_supplier_missing_vat": 0.05,
}

# Proportion of employees who have left the business.
LEAVER_RATE = 0.12

# Proportion of cost centres closed during reorganisation.
CLOSED_COST_CENTRE_RATE = 0.20

# Proportion of finance client accounts that have been closed.
CLOSED_ACCOUNT_RATE = 0.15