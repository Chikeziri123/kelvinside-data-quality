"""
Inspect the DQ-CRM-004 duplicate client findings.

Purpose is to separate true duplicates, the same organisation entered
twice, from false positives caused by name normalisation collapsing two
genuinely different entities. The catalogue rejects rules whose false
positive rate erodes steward trust, so the rule has to be held to that
same standard.

Run from the project root:
    python -m src.quality.inspect_duplicates
"""

import duckdb

from ..generator.config import PROJECT_ROOT

DB_PATH = PROJECT_ROOT / "data" / "warehouse" / "kelvinside.duckdb"

QUERY = """
select
    d.client_name_normalised,
    d.record_count,
    string_agg(s.client_name, ' / ') as actual_names
from main_dq_failures.dq_crm_004_duplicate_client_records d
join main_staging.stg_crm_clients s
    on s.client_name_normalised = d.client_name_normalised
group by 1, 2
order by 2 desc, 1
"""


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    total = con.execute(
        "select count(*) from main_dq_failures.dq_crm_004_duplicate_client_records"
    ).fetchone()[0]
    print(f"Duplicate groups flagged: {total}\n")

    for normalised, count, names in con.execute(QUERY).fetchall():
        print(f"[{count}] {normalised}")
        print(f"     {names}")

    fin008 = con.execute(
        "select count(*) from main_dq_failures.dq_fin_008_invoice_number_unique"
    ).fetchone()[0]
    print(f"\nDQ-FIN-008 duplicate invoice numbers: {fin008}")


if __name__ == "__main__":
    main()