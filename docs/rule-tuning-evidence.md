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