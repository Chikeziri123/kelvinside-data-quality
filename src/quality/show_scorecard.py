"""
Prints the current rule results and open issues to the terminal.

A quick check during development, and the source of the numbers quoted in
the evidence pack. The Power BI scorecard in Phase 5 reads the same two
tables.

Run from the project root:
    python -m src.quality.show_scorecard
"""

import duckdb

from ..generator.config import PROJECT_ROOT

DB_PATH = PROJECT_ROOT / "data" / "warehouse" / "kelvinside.duckdb"


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    print("RULE RESULTS")
    print("-" * 78)
    rows = con.execute("""
        select rule_id, severity, failing_records, population_in_scope,
               population_total, failure_rate_pct, rule_status
        from main_marts.fct_rule_results
        order by is_breached desc, severity, rule_id
    """).fetchall()

    header = f"{'Rule':<12}{'Severity':<10}{'Fail':>6}{'Scope':>8}{'Total':>8}{'Rate %':>9}  Status"
    print(header)
    for rule, sev, fail, scope, total, rate, status in rows:
        print(f"{rule:<12}{sev:<10}{fail:>6}{scope:>8}{total:>8}{rate:>9}  {status}")

    print("\n\nWHERE THE SCOPED DENOMINATOR CHANGED THE RATE")
    print("-" * 78)
    scoped = con.execute("""
        select rule_id, population_in_scope, population_total,
               failure_rate_pct,
               round(100.0 * failing_records / population_total, 4) as rate_on_full_table
        from main_marts.fct_rule_results
        where population_in_scope < population_total
          and failing_records > 0
        order by failure_rate_pct - round(100.0 * failing_records / population_total, 4) desc
    """).fetchall()
    for rule, scope, total, scoped_rate, full_rate in scoped:
        print(f"{rule:<12} {scoped_rate:>8} % on {scope:>5} in scope"
              f"   vs {full_rate:>8} % on {total:>5} total")

    print("\n\nOPEN ISSUES")
    print("-" * 78)
    issues = con.execute("""
        select issue_id, severity, currently_assigned_to, sla_due_date,
               sla_status, failing_records
        from main_marts.fct_dq_issues
        order by severity, sla_due_date
    """).fetchall()
    for issue, sev, assignee, due, sla, records in issues:
        print(f"{issue:<26}{sev:<10}{records:>6} records  due {due}  {sla}")
        print(f"{'':26}assigned to {assignee}")

    summary = con.execute("""
        select
            count(*) filter (where rule_status = 'Clean'),
            count(*) filter (where rule_status = 'Within tolerance'),
            count(*) filter (where rule_status = 'Breached'),
            round(avg(pass_rate_pct), 2)
        from main_marts.fct_rule_results
    """).fetchone()

    print("\n\nSUMMARY")
    print("-" * 78)
    print(f"Clean rules:            {summary[0]}")
    print(f"Within tolerance:       {summary[1]}")
    print(f"Breached:               {summary[2]}")
    print(f"Mean pass rate:         {summary[3]} percent")


if __name__ == "__main__":
    main()