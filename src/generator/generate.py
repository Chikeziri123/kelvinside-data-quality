"""
Generates the three Kelvinside source extracts with defects seeded at
controlled rates, together with the defect manifest.

Generation order follows the real dependency chain:
cost centres, then employees, then clients and contacts, then finance
accounts, then invoices and opportunities. Cross system defects are
injected after both sides exist, which is the only way to create a
genuine referential break rather than a missing value.

Run from the project root:
    python -m src.generator.generate
"""

import random
from datetime import timedelta

from faker import Faker

from .common import (
    DefectManifest,
    pick_sample,
    random_date,
    uk_postcode,
    write_csv,
)
from .config import (
    CLOSED_ACCOUNT_RATE,
    CLOSED_COST_CENTRE_RATE,
    DEFECT_RATES,
    EXTRACT_DATE,
    LEAVER_RATE,
    RAW_DIR,
    SEED,
    VOLUMES,
)

fake = Faker("en_GB")

PRACTICES = [
    "Advisory",
    "Technology",
    "Risk and Assurance",
    "People and Change",
    "Corporate Finance",
]
OFFICES = ["Newcastle", "Manchester", "Glasgow"]
STAGES = ["Qualify", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
OPEN_STAGES = {"Qualify", "Proposal", "Negotiation"}


def build_cost_centres(rng, manifest):
    rows = []
    for index in range(1, VOLUMES["cost_centres"] + 1):
        opened = random_date(rng, EXTRACT_DATE.replace(year=2015), EXTRACT_DATE)
        rows.append(
            {
                "cost_centre_code": f"CC{index:03d}",
                "cost_centre_name": f"{rng.choice(PRACTICES)} {rng.choice(OFFICES)}",
                "practice": rng.choice(PRACTICES),
                "office": rng.choice(OFFICES),
                "status": "Open",
                "opened_date": opened,
                "closed_date": None,
            }
        )

    # A reorganisation closed a fifth of the cost centres. Nothing downstream
    # was updated, which is the root cause of two of the board's four issues.
    for row in pick_sample(rng, rows, CLOSED_COST_CENTRE_RATE):
        row["status"] = "Closed"
        row["closed_date"] = random_date(
            rng, EXTRACT_DATE - timedelta(days=540), EXTRACT_DATE - timedelta(days=30)
        )

    return rows


def build_employees(rng, manifest, cost_centres):
    open_codes = [c["cost_centre_code"] for c in cost_centres]
    rows = []

    for index in range(1, VOLUMES["employees"] + 1):
        first = fake.first_name()
        last = fake.last_name()
        start = random_date(
            rng, EXTRACT_DATE.replace(year=2015), EXTRACT_DATE - timedelta(days=30)
        )
        rows.append(
            {
                "employee_id": f"EMP{index:04d}",
                "first_name": first,
                "last_name": last,
                "work_email": f"{first}.{last}@kelvinside.co.uk".lower(),
                "job_title": fake.job()[:60],
                "office": rng.choice(OFFICES),
                "cost_centre_code": rng.choice(open_codes),
                "start_date": start,
                "leaver_date": None,
                "employment_status": "Active",
                "last_updated": random_date(
                    rng, EXTRACT_DATE - timedelta(days=400), EXTRACT_DATE
                ),
            }
        )

    for row in pick_sample(rng, rows, LEAVER_RATE):
        row["employment_status"] = "Leaver"
        row["leaver_date"] = random_date(
            rng, row["start_date"] + timedelta(days=90), EXTRACT_DATE
        )

    _seed_hr_defects(rng, manifest, rows)
    return rows


def _seed_hr_defects(rng, manifest, employees):
    for row in pick_sample(rng, employees, DEFECT_RATES["hr_missing_email"]):
        row["work_email"] = None
        manifest.record(
            "Brackenhill HR", "hr_employees", row["employee_id"], "work_email",
            "missing_mandatory_value", "Completeness", "DQ-HR-001",
            "Payslip and system access notifications cannot be delivered",
        )

    for row in pick_sample(rng, employees, DEFECT_RATES["hr_invalid_email"]):
        row["work_email"] = row["work_email"].replace("@", ".") if row["work_email"] else "no.at.sign"
        manifest.record(
            "Brackenhill HR", "hr_employees", row["employee_id"], "work_email",
            "invalid_format", "Validity", "DQ-HR-002",
            "Automated communications bounce without anyone being alerted",
        )

    for row in pick_sample(rng, employees, DEFECT_RATES["hr_orphan_cost_centre"]):
        row["cost_centre_code"] = f"CC{rng.randint(900, 999)}"
        manifest.record(
            "Brackenhill HR", "hr_employees", row["employee_id"], "cost_centre_code",
            "broken_reference", "Referential integrity", "DQ-HR-003",
            "Employee cost falls outside practice profitability reporting",
        )

    for row in pick_sample(rng, employees, DEFECT_RATES["hr_missing_start_date"]):
        row["start_date"] = None
        manifest.record(
            "Brackenhill HR", "hr_employees", row["employee_id"], "start_date",
            "missing_mandatory_value", "Completeness", "DQ-HR-004",
            "Service length, holiday accrual and probation dates cannot be calculated",
        )

    for row in pick_sample(rng, employees, DEFECT_RATES["hr_future_start_date"]):
        row["start_date"] = EXTRACT_DATE + timedelta(days=rng.randint(30, 400))
        row["employment_status"] = "Active"
        manifest.record(
            "Brackenhill HR", "hr_employees", row["employee_id"], "start_date",
            "implausible_date", "Validity", "DQ-HR-005",
            "Headcount is overstated by people who have not yet joined",
        )


def build_clients(rng, manifest, employees):
    active_ids = [e["employee_id"] for e in employees if e["employment_status"] == "Active"]
    leaver_ids = [e["employee_id"] for e in employees if e["employment_status"] == "Leaver"]
    rows = []

    for index in range(1, VOLUMES["clients"] + 1):
        created = random_date(
            rng, EXTRACT_DATE.replace(year=2016), EXTRACT_DATE - timedelta(days=15)
        )
        rows.append(
            {
                "client_id": f"CL{index:05d}",
                "client_name": fake.company(),
                "postcode": uk_postcode(rng),
                "industry": fake.bs().split()[0].title(),
                "account_manager_employee_id": rng.choice(active_ids),
                "status": "Active",
                "created_date": created,
                "last_updated": random_date(rng, created, EXTRACT_DATE),
            }
        )

    _seed_client_defects(rng, manifest, rows, leaver_ids)
    return rows


def _seed_client_defects(rng, manifest, clients, leaver_ids):
    for row in pick_sample(rng, clients, DEFECT_RATES["crm_invalid_postcode"]):
        row["postcode"] = rng.choice(["00000", "N/A", "TBC", "123 456"])
        manifest.record(
            "Halstead CRM", "crm_clients", row["client_id"], "postcode",
            "invalid_format", "Validity", "DQ-CRM-001",
            "Client correspondence and territory assignment fail",
        )

    for row in pick_sample(rng, clients, DEFECT_RATES["crm_missing_account_manager"]):
        row["account_manager_employee_id"] = None
        manifest.record(
            "Halstead CRM", "crm_clients", row["client_id"], "account_manager_employee_id",
            "missing_mandatory_value", "Completeness", "DQ-CRM-002",
            "Nobody is accountable for the client relationship",
        )

    for row in pick_sample(rng, clients, DEFECT_RATES["crm_leaver_account_manager"]):
        if leaver_ids:
            row["account_manager_employee_id"] = rng.choice(leaver_ids)
            manifest.record(
                "Halstead CRM", "crm_clients", row["client_id"],
                "account_manager_employee_id", "reference_to_inactive_party",
                "Consistency", "DQ-CRM-003",
                "Client is owned by someone who has left, so contact lapses",
            )

    # Duplicate client records: same organisation entered twice with a
    # legal suffix variation. This is the root cause of understated credit
    # exposure, because no single view of the client balance exists.
    next_index = len(clients)
    for row in pick_sample(rng, clients, DEFECT_RATES["crm_duplicate_client"]):
        next_index += 1
        variant = row["client_name"].replace("Ltd", "Limited").replace("PLC", "Plc")
        if variant == row["client_name"]:
            variant = f"{row['client_name']} Limited"
        duplicate = dict(row)
        duplicate["client_id"] = f"CL{next_index:05d}"
        duplicate["client_name"] = variant
        duplicate["created_date"] = row["created_date"] + timedelta(days=rng.randint(20, 600))
        duplicate["last_updated"] = EXTRACT_DATE - timedelta(days=rng.randint(1, 120))
        clients.append(duplicate)
        manifest.record(
            "Halstead CRM", "crm_clients", duplicate["client_id"], "client_name",
            "duplicate_entity", "Uniqueness", "DQ-CRM-004",
            f"Credit exposure split across {row['client_id']} and {duplicate['client_id']}",
        )


def build_contacts(rng, manifest, clients):
    client_ids = [c["client_id"] for c in clients]
    rows = []
    for index in range(1, VOLUMES["contacts"] + 1):
        rows.append(
            {
                "contact_id": f"CT{index:05d}",
                "client_id": rng.choice(client_ids),
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "is_primary": rng.choice(["Y", "N"]),
                "last_updated": random_date(
                    rng, EXTRACT_DATE - timedelta(days=500), EXTRACT_DATE
                ),
            }
        )

    for row in pick_sample(rng, rows, DEFECT_RATES["crm_missing_contact_email"]):
        row["email"] = None
        manifest.record(
            "Halstead CRM", "crm_contacts", row["contact_id"], "email",
            "missing_mandatory_value", "Completeness", "DQ-CRM-005",
            "Contact cannot be reached by campaign or engagement communications",
        )

    for row in pick_sample(rng, rows, DEFECT_RATES["crm_contact_orphan_client"]):
        row["client_id"] = f"CL{rng.randint(90000, 99999)}"
        manifest.record(
            "Halstead CRM", "crm_contacts", row["contact_id"], "client_id",
            "broken_reference", "Referential integrity", "DQ-CRM-006",
            "Contact is invisible on the client record it belongs to",
        )

    return rows


def build_opportunities(rng, manifest, clients, employees):
    client_ids = [c["client_id"] for c in clients]
    active_ids = [e["employee_id"] for e in employees if e["employment_status"] == "Active"]
    leaver_ids = [e["employee_id"] for e in employees if e["employment_status"] == "Leaver"]
    rows = []

    for index in range(1, VOLUMES["opportunities"] + 1):
        created = random_date(
            rng, EXTRACT_DATE - timedelta(days=900), EXTRACT_DATE - timedelta(days=5)
        )
        stage = rng.choice(STAGES)
        rows.append(
            {
                "opportunity_id": f"OP{index:05d}",
                "client_id": rng.choice(client_ids),
                "opportunity_name": f"{rng.choice(PRACTICES)} engagement",
                "stage": stage,
                "value_gbp": round(rng.uniform(5_000, 450_000), 2),
                "expected_close_date": created + timedelta(days=rng.randint(30, 240)),
                "owner_employee_id": rng.choice(active_ids),
                "created_date": created,
                "last_updated": random_date(rng, created, EXTRACT_DATE),
            }
        )

    for row in pick_sample(rng, rows, DEFECT_RATES["crm_leaver_owner"]):
        if leaver_ids:
            row["owner_employee_id"] = rng.choice(leaver_ids)
            row["stage"] = rng.choice(sorted(OPEN_STAGES))
            manifest.record(
                "Halstead CRM", "crm_opportunities", row["opportunity_id"],
                "owner_employee_id", "reference_to_inactive_party", "Consistency",
                "DQ-CRM-007",
                "Open pipeline is owned by a leaver, so the opportunity goes unworked",
            )

    for row in pick_sample(rng, rows, DEFECT_RATES["crm_stale_open_opportunity"]):
        row["stage"] = rng.choice(sorted(OPEN_STAGES))
        row["last_updated"] = EXTRACT_DATE - timedelta(days=rng.randint(200, 500))
        manifest.record(
            "Halstead CRM", "crm_opportunities", row["opportunity_id"], "last_updated",
            "stale_record", "Timeliness", "DQ-CRM-008",
            "Pipeline forecast includes opportunities nobody has touched for months",
        )

    for row in pick_sample(rng, rows, DEFECT_RATES["crm_opportunity_orphan_client"]):
        row["client_id"] = f"CL{rng.randint(90000, 99999)}"
        manifest.record(
            "Halstead CRM", "crm_opportunities", row["opportunity_id"], "client_id",
            "broken_reference", "Referential integrity", "DQ-CRM-009",
            "Revenue forecast cannot be attributed to a client",
        )

    return rows


def build_client_accounts(rng, manifest, clients):
    rows = []
    for index, client in enumerate(clients, start=1):
        opened = client["created_date"]
        rows.append(
            {
                "account_id": f"ACC{index:05d}",
                "crm_client_ref": client["client_id"],
                "account_name": client["client_name"],
                "status": "Open",
                "credit_limit_gbp": round(rng.uniform(10_000, 500_000), 2),
                "opened_date": opened,
                "closed_date": None,
            }
        )

    for row in pick_sample(rng, rows, CLOSED_ACCOUNT_RATE):
        row["status"] = "Closed"
        row["closed_date"] = random_date(
            rng, EXTRACT_DATE - timedelta(days=700), EXTRACT_DATE - timedelta(days=20)
        )

    for row in pick_sample(rng, rows, DEFECT_RATES["fin_account_orphan_client"]):
        row["crm_client_ref"] = f"CL{rng.randint(90000, 99999)}"
        manifest.record(
            "Trentmoor Finance", "finance_client_accounts", row["account_id"],
            "crm_client_ref", "broken_reference", "Referential integrity", "DQ-FIN-001",
            "Finance account cannot be reconciled to any CRM client",
        )

    return rows


def build_suppliers(rng, manifest):
    rows = []
    for index in range(1, VOLUMES["suppliers"] + 1):
        rows.append(
            {
                "supplier_id": f"SUP{index:04d}",
                "supplier_name": fake.company(),
                "vat_number": f"GB{rng.randint(100000000, 999999999)}",
                "payment_terms_days": rng.choice([14, 30, 45, 60]),
                "status": rng.choice(["Active", "Active", "Active", "Dormant"]),
            }
        )

    for row in pick_sample(rng, rows, DEFECT_RATES["fin_supplier_missing_vat"]):
        row["vat_number"] = None
        manifest.record(
            "Trentmoor Finance", "finance_suppliers", row["supplier_id"], "vat_number",
            "missing_mandatory_value", "Completeness", "DQ-FIN-002",
            "VAT cannot be reclaimed and the HMRC return is understated",
        )

    return rows


def build_invoices(rng, manifest, accounts, cost_centres):
    open_accounts = [a for a in accounts if a["status"] == "Open"]
    closed_accounts = [a for a in accounts if a["status"] == "Closed"]
    open_codes = [c["cost_centre_code"] for c in cost_centres if c["status"] == "Open"]
    closed_codes = [c["cost_centre_code"] for c in cost_centres if c["status"] == "Closed"]
    rows = []

    for index in range(1, VOLUMES["invoices"] + 1):
        invoice_date = random_date(
            rng, EXTRACT_DATE - timedelta(days=400), EXTRACT_DATE - timedelta(days=1)
        )
        account = rng.choice(open_accounts)
        rows.append(
            {
                "invoice_number": f"INV{index:06d}",
                "account_id": account["account_id"],
                "invoice_date": invoice_date,
                "due_date": invoice_date + timedelta(days=rng.choice([14, 30, 45])),
                "amount_gbp": round(rng.uniform(500, 95_000), 2),
                "status": rng.choice(["Paid", "Paid", "Open", "Open", "Disputed"]),
                "cost_centre_code": rng.choice(open_codes),
                "last_updated": invoice_date + timedelta(days=rng.randint(0, 40)),
            }
        )

    # The headline finding: invoices raised against accounts finance closed.
    for row in pick_sample(rng, rows, DEFECT_RATES["fin_invoice_closed_account"]):
        if closed_accounts:
            account = rng.choice(closed_accounts)
            row["account_id"] = account["account_id"]
            manifest.record(
                "Trentmoor Finance", "finance_invoices", row["invoice_number"],
                "account_id", "reference_to_closed_entity", "Consistency", "DQ-FIN-003",
                "Invoice raised against a closed account, creating write-off risk",
            )

    for row in pick_sample(rng, rows, DEFECT_RATES["fin_invoice_orphan_account"]):
        row["account_id"] = f"ACC{rng.randint(90000, 99999)}"
        manifest.record(
            "Trentmoor Finance", "finance_invoices", row["invoice_number"], "account_id",
            "broken_reference", "Referential integrity", "DQ-FIN-004",
            "Revenue cannot be attributed to a client account",
        )

    for row in pick_sample(rng, rows, DEFECT_RATES["fin_invoice_dead_cost_centre"]):
        if closed_codes:
            row["cost_centre_code"] = rng.choice(closed_codes)
            manifest.record(
                "Trentmoor Finance", "finance_invoices", row["invoice_number"],
                "cost_centre_code", "reference_to_closed_entity", "Consistency",
                "DQ-FIN-005",
                "Revenue posted to a closed cost centre distorts practice profitability",
            )

    for row in pick_sample(rng, rows, DEFECT_RATES["fin_negative_amount"]):
        row["amount_gbp"] = -abs(row["amount_gbp"])
        manifest.record(
            "Trentmoor Finance", "finance_invoices", row["invoice_number"], "amount_gbp",
            "value_out_of_range", "Validity", "DQ-FIN-006",
            "Negative invoice without a credit note reference understates revenue",
        )

    for row in pick_sample(rng, rows, DEFECT_RATES["fin_due_before_invoice_date"]):
        row["due_date"] = row["invoice_date"] - timedelta(days=rng.randint(1, 20))
        manifest.record(
            "Trentmoor Finance", "finance_invoices", row["invoice_number"], "due_date",
            "illogical_date_sequence", "Validity", "DQ-FIN-007",
            "Invoice appears overdue on issue, triggering incorrect chasing",
        )

    # Duplicate invoice numbers, which break the assumption that the
    # invoice number is a usable business key.
    duplicates = []
    for row in pick_sample(rng, rows, DEFECT_RATES["fin_duplicate_invoice_number"]):
        clone = dict(row)
        clone["amount_gbp"] = round(row["amount_gbp"] + rng.uniform(-50, 50), 2)
        clone["last_updated"] = row["last_updated"] + timedelta(days=1)
        duplicates.append(clone)
        manifest.record(
            "Trentmoor Finance", "finance_invoices", row["invoice_number"],
            "invoice_number", "duplicate_key", "Uniqueness", "DQ-FIN-008",
            "The same invoice number appears twice with different values",
        )
    rows.extend(duplicates)

    return rows


TABLES = {
    "finance_cost_centres": [
        "cost_centre_code", "cost_centre_name", "practice", "office",
        "status", "opened_date", "closed_date",
    ],
    "hr_employees": [
        "employee_id", "first_name", "last_name", "work_email", "job_title",
        "office", "cost_centre_code", "start_date", "leaver_date",
        "employment_status", "last_updated",
    ],
    "crm_clients": [
        "client_id", "client_name", "postcode", "industry",
        "account_manager_employee_id", "status", "created_date", "last_updated",
    ],
    "crm_contacts": [
        "contact_id", "client_id", "first_name", "last_name", "email",
        "phone", "is_primary", "last_updated",
    ],
    "crm_opportunities": [
        "opportunity_id", "client_id", "opportunity_name", "stage",
        "value_gbp", "expected_close_date", "owner_employee_id",
        "created_date", "last_updated",
    ],
    "finance_client_accounts": [
        "account_id", "crm_client_ref", "account_name", "status",
        "credit_limit_gbp", "opened_date", "closed_date",
    ],
    "finance_suppliers": [
        "supplier_id", "supplier_name", "vat_number", "payment_terms_days", "status",
    ],
    "finance_invoices": [
        "invoice_number", "account_id", "invoice_date", "due_date",
        "amount_gbp", "status", "cost_centre_code", "last_updated",
    ],
}


def main():
    rng = random.Random(SEED)
    Faker.seed(SEED)
    manifest = DefectManifest()

    cost_centres = build_cost_centres(rng, manifest)
    employees = build_employees(rng, manifest, cost_centres)
    clients = build_clients(rng, manifest, employees)
    contacts = build_contacts(rng, manifest, clients)
    opportunities = build_opportunities(rng, manifest, clients, employees)
    accounts = build_client_accounts(rng, manifest, clients)
    suppliers = build_suppliers(rng, manifest)
    invoices = build_invoices(rng, manifest, accounts, cost_centres)

    data = {
        "finance_cost_centres": cost_centres,
        "hr_employees": employees,
        "crm_clients": clients,
        "crm_contacts": contacts,
        "crm_opportunities": opportunities,
        "finance_client_accounts": accounts,
        "finance_suppliers": suppliers,
        "finance_invoices": invoices,
    }

    print(f"Writing extracts to {RAW_DIR}")
    for name, rows in data.items():
        write_csv(f"{name}.csv", TABLES[name], rows)
        print(f"  {name:28} {len(rows):>6} rows")

    manifest.write()
    print(f"\nSeeded defects: {len(manifest)}")
    for defect_type, count in manifest.summary().items():
        print(f"  {defect_type:32} {count:>5}")


if __name__ == "__main__":
    main()