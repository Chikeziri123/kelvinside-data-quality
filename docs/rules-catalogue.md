# Kelvinside Data Quality Rules Catalogue

Version 1.0, effective 21 September 2026.

Every rule in this catalogue has an owner, a threshold and a stated
business consequence. A rule that nobody owns and that cannot be linked to
a consequence does not belong here, because it will never be actioned and
will only dilute the score.

## Quality dimensions in use

| Dimension | Question it answers |
|---|---|
| Completeness | Is the value present where the business requires one? |
| Validity | Does the value conform to an expected format, range or sequence? |
| Uniqueness | Does the record appear exactly once? |
| Referential integrity | Does the reference point at a record that exists? |
| Consistency | Do the systems agree, and does the record agree with itself? |
| Timeliness | Has the record been maintained recently enough to be trusted? |

## Severity and response

Severity is set by consequence, not by volume. A single invoice raised
against a closed account is more serious than fifty missing phone numbers.

| Severity | Meaning | Threshold | Resolution SLA |
|---|---|---|---|
| Critical | Financial loss, regulatory exposure or external client impact | 0.0 percent | 2 working days |
| High | Materially wrong reporting or a broken downstream process | 0.5 percent | 5 working days |
| Medium | Operational friction, workaround exists | 2.0 percent | 20 working days |
| Low | Cosmetic or low value completeness | 5.0 percent | Next quarterly review |

Threshold is the proportion of failing records above which the rule is
reported as breached. Non-zero thresholds are a deliberate choice: chasing
the last tenth of a percent on a Low rule costs more than it returns.

## Escalation

A breached rule creates an issue assigned to the operational steward. If
the SLA elapses without resolution, the issue escalates to the accountable
owner and appears on the Operations Board exception page. Cost centre
rules escalate to the Finance Director, since cost centre is shared data
and disputes between Finance and HR otherwise stall.

---

## Brackenhill HR

| Rule ID | Dimension | Rule | Severity | Threshold | Owner | Consequence if breached |
|---|---|---|---|---|---|---|
| DQ-HR-001 | Completeness | Every active employee has a work email address | High | 0.5% | HR Director | Payslip and access notifications are undeliverable |
| DQ-HR-002 | Validity | Work email matches a valid address format | Medium | 2.0% | HR Director | Automated communications bounce silently |
| DQ-HR-003 | Referential integrity | Employee cost centre exists in the finance cost centre list | High | 0.5% | Finance Director | Employee cost falls outside practice profitability |
| DQ-HR-004 | Completeness | Every employee has a start date | High | 0.5% | HR Director | Service length, accrual and probation cannot be calculated |
| DQ-HR-005 | Validity | Start date is not in the future for an active employee | Medium | 2.0% | HR Director | Headcount overstated by people who have not joined |
| DQ-HR-006 | Validity | Leaver date is on or after the start date | High | 0.5% | HR Director | Employment periods are nonsensical in reporting |
| DQ-HR-007 | Consistency | An employee with a leaver date is not marked Active | High | 0.5% | HR Director | Leavers retain system access and appear in headcount |

## Halstead CRM

| Rule ID | Dimension | Rule | Severity | Threshold | Owner | Consequence if breached |
|---|---|---|---|---|---|---|
| DQ-CRM-001 | Validity | Client postcode matches UK postcode format | Medium | 2.0% | Commercial Director | Correspondence fails and territory assignment is wrong |
| DQ-CRM-002 | Completeness | Every active client has an account manager | High | 0.5% | Commercial Director | Nobody is accountable for the relationship |
| DQ-CRM-003 | Consistency | Client account manager is an active employee | High | 0.5% | Commercial Director | Client is owned by a leaver and contact lapses |
| DQ-CRM-004 | Uniqueness | No duplicate client organisations by normalised name and postcode | Critical | 0.0% | Commercial Director | Credit exposure is split and understated |
| DQ-CRM-005 | Completeness | Every contact has an email address | Low | 5.0% | Commercial Director | Contact is unreachable for engagement communications |
| DQ-CRM-006 | Referential integrity | Contact references a client that exists | High | 0.5% | Commercial Director | Contact is invisible on the client record |
| DQ-CRM-007 | Consistency | Open opportunities are owned by an active employee | Critical | 0.0% | Commercial Director | Live pipeline goes unworked after a leaver departs |
| DQ-CRM-008 | Timeliness | Open opportunities updated within the last 180 days | Medium | 2.0% | Commercial Director | Forecast includes pipeline nobody has touched |
| DQ-CRM-009 | Referential integrity | Opportunity references a client that exists | High | 0.5% | Commercial Director | Revenue forecast cannot be attributed to a client |
| DQ-CRM-010 | Validity | Opportunity value is greater than zero | Medium | 2.0% | Commercial Director | Pipeline value is distorted |

## Trentmoor Finance

| Rule ID | Dimension | Rule | Severity | Threshold | Owner | Consequence if breached |
|---|---|---|---|---|---|---|
| DQ-FIN-001 | Referential integrity | Finance client account references a CRM client that exists | High | 0.5% | Finance Director | Account cannot be reconciled to any client |
| DQ-FIN-002 | Completeness | Active suppliers have a VAT number | Medium | 2.0% | Finance Director | VAT cannot be reclaimed and the return is understated |
| DQ-FIN-003 | Consistency | Invoices are not raised against closed accounts | Critical | 0.0% | Finance Director | Write-off risk and client relationship damage |
| DQ-FIN-004 | Referential integrity | Invoice references an account that exists | High | 0.5% | Finance Director | Revenue cannot be attributed to a client account |
| DQ-FIN-005 | Consistency | Invoices are not posted to closed cost centres | Critical | 0.0% | Finance Director | Practice profitability is materially misstated |
| DQ-FIN-006 | Validity | Invoice amount is greater than zero | High | 0.5% | Finance Director | Negative invoices without credit notes understate revenue |
| DQ-FIN-007 | Validity | Invoice due date is on or after the invoice date | Medium | 2.0% | Finance Director | Invoices appear overdue on issue and are chased wrongly |
| DQ-FIN-008 | Uniqueness | Invoice number appears exactly once | Critical | 0.0% | Finance Director | The business key is unreliable and duplicates are paid |
| DQ-FIN-009 | Validity | Credit limit is within the approved range | Low | 5.0% | Finance Director | Credit control operates on unapproved limits |

---

## Rules deliberately excluded from version 1.0

Recording what was left out, and why, matters as much as what was
included. Three candidates were rejected at the design stage:

1. **Phone number format validation.** UK phone formats vary widely and
   the business accepts several. The false positive rate would exceed the
   genuine finding rate, which erodes trust in the whole scorecard.
2. **Cross system client name matching.** Fuzzy matching between CRM and
   Finance names would find real breaks, but without a confidence
   threshold agreed with the Commercial Director it produces unactionable
   volume. Deferred to version 1.1 with a review step.
3. **Invoice amount outlier detection.** Statistically attractive, but a
   large invoice is not a defect and treating it as one would train
   stewards to dismiss alerts.

The principle: a rule earns its place only if a steward can act on a
failure. Anything else is noise dressed as governance.

## Review cycle

The catalogue is reviewed quarterly by the data owners. Rules can be
added, retired or have thresholds changed, and every change is recorded
with the rationale. Thresholds tighten as scores improve, so the standard
rises rather than the target being permanently met.