# Rule tuning evidence

Findings that changed a rule after implementation, with the measurement
that justified the change. Kept separate from the decision records so the
raw before and after numbers stay visible.

## DQ-CRM-004, duplicate client detection

Sample of false positives under name-only matching, removed by requiring
a postcode match:

```
[6] jones   Jones PLC / Jones PLC / Jones Group / Jones Group / Jones Ltd / Jones Ltd
[6] smith   Smith Group / Smith PLC / Smith Group / Smith Ltd / Smith PLC / Smith Group
[3] evans   Evans PLC / Evans PLC / Evans Group
[2] brown   Brown PLC / Brown Group
[2] lloyd   Lloyd Group / Lloyd PLC
```

Sample of true positives retained after the change:

```
[2] barlowturner   Barlow-Turner / Barlow-Turner Limited
[2] hussaininc     Hussain Inc / Hussain Inc Limited
[2] griffinllc     Griffin LLC / Griffin LLC Limited
```

Outcome: 37 groups reduced to 18, all true positives. Full reasoning in
ADR-002.

## Cascading defect observed in Brackenhill HR

EMP0251 carries a start date of 14 May 2027, a leaver date of 9 November
2019, and an employment status of Active.

One injected defect, an implausible future start date, produced failures
against three separate rules: DQ-HR-005 on the future date, DQ-HR-006 on
the leaver date preceding the start date, and DQ-HR-007 on a leaver
record still marked Active.

This is worth recording because it demonstrates something the scorecard
cannot show on its own. Rule failure counts are not independent, so a
domain score that improves by three points after one record is fixed is
not evidence of three fixes. Root cause tagging in the issue lifecycle
exists precisely to make that visible, otherwise remediation effort is
credited to the wrong place.
## DQ-CRM-008 investigation and a denominator defect

The rule reported 290 failures at 32 percent against a seeded rate of 6
percent. Investigation showed the rule is correct: 290 of 562 open
opportunities have genuinely not been updated in 180 days. The age
distribution is close to uniform, so the seeded staleness sits on top of
a population that was already ageing.

The investigation exposed a separate defect in the results mart. The
population figure is taken from the full staging model, but rules with a
where clause only examine a subset. DQ-CRM-008 examines open
opportunities only, so the true rate is 290 of 562, or 51.6 percent, not
290 of 900. Every filtered rule is currently understating its failure
rate, which means a rule can appear within tolerance when it is not.

Thresholds tested against the open pipeline:

```8
  90 days   398 flagged   70.8 percent
 180 days   290 flagged   51.6 percent
 270 days   214 flagged   38.1 percent
 365 days   143 flagged   25.4 percent
 540 days    57 flagged   10.1 percent
```8

To be resolved before the scorecard is published, since the scorecard
would otherwise present understated rates as fact.

## Denominator defect: three suppressed breaches

The scoped denominator change moved three rules from within tolerance to
breached, and changed no rule in the opposite direction.

| Rule | Full table | In scope | Threshold |
|---|---|---|---|
| DQ-HR-006 | 0.50% on 400 | 4.26% on 47 | 0.5% |
| DQ-HR-007 | 0.50% on 400 | 4.17% on 48 | 0.5% |
| DQ-HR-002 | 2.00% on 400 | 2.06% on 388 | 2.0% |

Breached rules rose from 18 to 21. Mean pass rate fell from 96.63 to
95.42 percent, which is the correct direction: the earlier figure was
flattered by counting records no rule had examined.

Note that the two HR-006 and HR-007 failures both originate from the
single cascading defect on EMP0251 recorded above. One bad record, three
rule breaches, two of which were invisible before this change.