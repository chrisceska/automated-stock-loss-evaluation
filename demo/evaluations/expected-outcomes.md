# Expected Outcomes

Use this file as the baseline when validating the Foundry demo.

## store-201-pos-decrement-failure

- Detection should classify the issue as `missing_decrement`.
- Evidence should show POS sales activity without a corresponding inventory decrement event.
- Root cause should rank POS-to-inventory sync failure first.
- Confidence should land in the high band, above the 85% auto-execution threshold.
- Decisioning should approve low-risk automated actions only.
- Execution should create a ticket, notify the store manager, and trigger a cycle count.

## store-118-receiving-gap

- Detection should classify the issue as `receiving_posting_gap` or an equivalent receiving mismatch.
- Evidence should connect the shipment confirmation to a missing ERP posting timestamp.
- Root cause should rank receiving synchronization failure above theft or manual counting error.
- Confidence should land in the medium band, between 70% and 84%.
- Decisioning should automate notification and ticketing, then require human review before any broader remediation.

## store-044-recurring-shrink-pattern

- Detection should identify a repeat pattern rather than a one-time transaction defect.
- Evidence should surface prior incidents, weekend clustering, and weak preventative controls.
- Root cause should point to recurring shrink risk caused by operational control gaps.
- Confidence should remain below full auto-remediation because direct causality is weaker than in the first scenario.
- Decisioning should escalate while still allowing preventative recommendations and pattern flagging.
- Prevention should recommend targeted controls such as lockbox coverage, weekend staffing review, and focused cycle counts.