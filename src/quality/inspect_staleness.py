"""
Investigates the DQ-CRM-008 staleness finding.

The rule reported a 32 percent failure rate against a seeded rate of 6
percent. Either the rule is over-firing, or the population genuinely
contains more stale records than were deliberately planted. The
distinction matters: one is a rule defect, the other is a finding.

Run from the project root:
    python -m src.quality.inspect_staleness
"""

import duckdb

from ..generator.config import PROJECT_ROOT

DB_PATH = PROJECT_ROOT / "data" / "warehouse" / "kelvinside.duckdb"


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    print("OPEN OPPORTUNITIES BY AGE SINCE LAST UPDATE")
    print("-" * 70)
    bands = con.execute("""
        select
            case
                when days_old < 90 then 'a. Under 90 days'
                when days_old < 180 then 'b. 90 to 179 days'
                when days_old < 365 then 'c. 180 to 364 days'
                else 'd. 365 days or more'
            end as age_band,
            count(*) as opportunities,
            round(sum(value_gbp) / 1000, 0) as value_k_gbp
        from (
            select
                value_gbp,
                date_diff('day', last_updated, date '2026-09-20') as days_old
            from main_staging.stg_crm_opportunities
            where is_open and last_updated is not null
        )
        group by 1
        order by 1
    """).fetchall()

    for band, count, value in bands:
        print(f"{band:<24}{count:>6} opportunities   GBP {value:>8,.0f}k")

    total_open = con.execute("""
        select count(*) from main_staging.stg_crm_opportunities where is_open
    """).fetchone()[0]
    print(f"\nTotal open opportunities: {total_open}")

    print("\n\nEFFECT OF DIFFERENT STALENESS THRESHOLDS")
    print("-" * 70)
    for threshold in (90, 180, 270, 365, 540):
        count = con.execute(f"""
            select count(*)
            from main_staging.stg_crm_opportunities
            where is_open
              and last_updated < date '2026-09-20' - interval {threshold} day
        """).fetchone()[0]
        pct = round(100.0 * count / total_open, 1)
        print(f"{threshold:>4} days   {count:>5} flagged   {pct:>5}% of open pipeline")


if __name__ == "__main__":
    main()