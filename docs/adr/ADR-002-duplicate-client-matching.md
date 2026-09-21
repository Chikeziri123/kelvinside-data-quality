# ADR-002: Match duplicate clients on normalised name and postcode together

Status: Accepted
Date: 21 September 2026
Rule affected: DQ-CRM-004 (Critical)

## Context

Duplicate client records split credit exposure across two accounts, so the
firm's true exposure to an organisation is understated. The Operations
Board raised this as one of four priority findings, which is why the rule
carries Critical severity and a zero percent threshold.

Detection needs a match key, because the duplicate is never an exact
string match. The same organisation is entered as "Barlow-Turner" on one
occasion and "Barlow-Turner Limited" on another.

## Problem

The first implementation normalised the client name by lowercasing,
removing punctuation, and stripping a list of trailing suffixes: Ltd,
Limited, PLC, LLP, Group and Holdings. Matching was on that normalised
name alone.

It flagged 37 groups against 18 known duplicates. Inspection of the
failures showed why:

| Pattern | Example | Verdict |
|---|---|---|
| Suffix variation | Barlow-Turner / Barlow-Turner Limited | True positive |
| Different legal entities collapsed | Jones PLC / Jones Group / Jones Ltd | False positive |
| Identical names, different organisations | Hill Ltd / Hill Ltd | Unresolvable on name alone |

Stripping Group and Holdings was the root cause. "Jones Group" and
"Jones Ltd" are separate legal entities, not a data entry variation of
one another. Roughly half of all findings were unactionable.

An unactionable Critical finding is worse than no finding. A steward who
investigates three false alarms stops investigating, and the rule's real
detections are lost with the noise. The catalogue's own admission
principle states that a rule earns its place only if a steward can act on
a failure, and the first implementation failed that test.

## Decision

Two changes:

1. Strip only the suffixes that denote the same legal entity written
   differently: Ltd and Limited. Group, Holdings, LLC, Inc and PLC are
   retained as part of the identity.
2. Require an identical postcode in addition to the normalised name
   match. Two organisations sharing a surname rarely share a registered
   address.

## Result

| Measure | Before | After |
|---|---|---|
| Groups flagged | 37 | 18 |
| True positives | 18 | 18 |
| False positives | 19 | 0 |
| Precision | 49% | 100% |
| Recall against seeded duplicates | 100% | 100% |

## Consequences

Positive:
- Every finding is actionable, so the Critical severity is honest.
- The finding can be sent straight to the CRM Administrator without a
  triage step in between.

Negative, and accepted knowingly:
- A genuine duplicate where the postcode was also mistyped will now be
  missed. Recall is traded for precision.
- Clients with a null postcode are excluded from the rule entirely. Those
  records are already caught by DQ-CRM-001, so the gap is covered
  elsewhere, but the dependency between the two rules is now real and
  should be stated when either is retired.

## Alternatives considered

**Fuzzy name matching with a similarity threshold.** Would catch the
mistyped postcode case and more besides. Rejected for version 1.0 for the
reason already recorded in the catalogue: without a confidence threshold
agreed with the Commercial Director, it produces volume nobody has agreed
to work. Revisit in version 1.1 with a human review queue rather than a
direct assignment.

**Lowering severity to High and accepting the false positives.** Rejected.
Severity is set by consequence, not by how confident the rule is. The
correct response to low confidence is to fix the rule, not to downgrade
the consequence.

## Revisit when

A duplicate is reported by the business that this rule did not catch. That
event is the signal that the postcode requirement is costing more recall
than it is buying precision.