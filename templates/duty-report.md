# Duty Report Example

Use this behavior-first shape. Replace the example facts with observed evidence; never copy unverified counts or statuses.

Return only these seven fields. Do not append file lists, `Issues encountered`, tool-use notes, or any postscript unless the engineer explicitly requests them. Put a relevant no-execution constraint under **Status**, **Verification**, or **Engineer action**.

```markdown
## Duty Report
**Status:** Partial — validation blocked.
**Delivered:** S1 retries transient failures three times; S2 never retries permanent failures.
**Coverage:** 2/3; S3 blocked by unspecified duplicate-result ownership.
**Verification:** S1/S2 observed RED then GREEN. Full suite: 142 passed, 2 old failures.
**Decisions:** Permanent failures bypass retry to avoid duplicate charges.
**Risks or deviations:** S3 remains absent.
**Engineer action:** Define who stores duplicate results.
```
