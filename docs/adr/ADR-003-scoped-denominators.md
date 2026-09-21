# ADR-003: Measure failure rates against the population each rule examines

Status: Accepted
Date: 21 September 2026
Affects: all filtered rules, the results mart, the rules catalogue seed

## Context

Every rule carries a threshold expressed as a percentage of failing
records. The threshold decides whether a breach is raised, an issue is
created, and a steward is asked to spend time. The denominator used to
calculate that percentage therefore decides what work gets done.

Many rules examine a subset of their table rather than all of it.
DQ-HR-001 applies to active employees, not leavers. DQ-CRM-008 applies to
open opportunities, not closed ones. DQ-FIN-002 applies to active
suppliers only.

## Problem

The first implementation of the results mart counted every row in the
staging model as the denominator, regardless of the rule's filter. A rule
was being measured against records it had never examined.

The effect was not uniform. It was largest exactly where the filter was
most selective, which is where the rules tend to be most specific and
most serious:

| Rule | Rate on full table | Rate in scope | Threshold | Verdict changed |
|---|---|---|---|---|
| DQ-HR-006 | 0.50% | 4.26% | 0.5% | Within tolerance to Breached |
| DQ-HR-007 | 0.50% | 4.17% | 0.5% | Within tolerance to Breached |
| DQ-HR-002 | 2.00% | 2.06% | 2.0% | Within tolerance to Breached |
| DQ-CRM-008 | 32.22% | 51.60% | 2.0% | Breached either way |
| DQ-CRM-007 | 5.00% | 8.01% | 0.0% | Breached either way |

DQ-HR-006 is the clearest case. Two employees carry a leaver date that
precedes their start date, which is a nonsensical employment history.
Only 47 employees have both dates populated, so the rule examined 47
records and found 2 wrong. Measured against all 400 employees the rate
was exactly at threshold and no issue was raised. Measured against the 47
it examined, it is eight times the threshold.

Three rules were being silently suppressed.

## Decision

Each rule declares its population filter in the rules catalogue seed,
alongside its threshold, owner and SLA. The macro that assembles rule
results applies that filter when counting the denominator.

Two figures are produced and both are retained:

- `population_in_scope`, the rows the rule examines, used for the failure
  rate and the threshold verdict
- `population_total`, every row in the table, used to report scope
  coverage

The filter lives in the catalogue rather than the macro because it is
part of the rule's definition. A reader of the catalogue can see what a
rule examines without reading SQL, and the filter cannot drift away from
the rule it belongs to.

## Consequences

Positive:
- Rates are honest. A rule that fails 2 of 47 reports 4.26 percent.
- Breach verdicts are correct, and three genuine breaches are now visible.
- Scope coverage becomes a reportable measure in its own right: the
  scorecard can show what proportion of a table any rule watches at all,
  which is the question "what are we not looking at".

Negative:
- Thresholds set against the old, understated rates are now effectively
  tighter. The quarterly review should revisit them with this in mind,
  rather than assuming the standard has changed.
- A highly selective filter produces a small denominator, where a single
  failing record moves the rate sharply. Rules examining fewer than fifty
  records should be read alongside the absolute count, not the percentage
  alone.

## Alternatives considered

**Express thresholds as absolute record counts.** Removes the denominator
problem entirely. Rejected because a count does not scale: five failures
in a table of fifty is a crisis, five in a table of fifty thousand is
noise, and the business reasons in proportions.

**Derive the filter by parsing the test definitions.** Technically
possible and avoids declaring the filter twice. Rejected as fragile: the
filter would be inferred from implementation rather than stated as intent,
and a change to one would silently change the other.

## Revisit when

The quarterly catalogue review, where thresholds should be reconsidered
against scoped rates rather than carried over from the original setting.