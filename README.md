# Kelvinside Data Quality Observability Platform

Automated data quality monitoring, ownership and issue management across
three disconnected business systems in a mid-market professional services
firm.

## The problem

Kelvinside Professional Services runs a CRM, a finance system and an HR
system that were never integrated. Invoices are raised against closed
accounts, time is booked to dead cost centres, leavers still own live
opportunities, and duplicate client records hide credit exposure. Nobody
finds out until a month end investigation, and nobody owns the fix.

Full context: [docs/business-context.md](docs/business-context.md)

## What this builds

- A synthetic three system landscape with defects seeded at controlled rates
- A rules catalogue covering completeness, validity, uniqueness,
  referential integrity, consistency and timeliness
- Automated execution of those rules with results captured to history
- An issue lifecycle with owner, SLA, status and root cause
- A Power BI scorecard by domain, by owner and over time

## Stack

Python 3.11, Faker, DuckDB, dbt, Power BI. DuckDB is used so the whole
project clones and runs with no database server. In production this would
sit on Postgres or Microsoft Fabric, with the dbt layer unchanged.

## Status

| Phase | Description | Status |
|---|---|---|
| 0 | Foundations and scaffold | Complete |
| 1 | Synthetic landscape with seeded defects | Not started |
| 2 | Rules catalogue | Not started |
| 3 | Rule implementation in dbt | Not started |
| 4 | Issue lifecycle | Not started |
| 5 | Power BI scorecard | Not started |
| 6 | Evidence and operating model | Not started |
| 7 | Scheduling and hardening | Not started |

## Quick start