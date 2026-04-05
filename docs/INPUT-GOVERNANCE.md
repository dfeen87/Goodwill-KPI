# INPUT-GOVERNANCE.md — Goodwill KPI Framework

---

## 1. Purpose

This document defines the input governance model for the Goodwill KPI Framework.
Input governance is the set of standards, controls, and processes that ensure
every numeric value supplied to the goodwill equations is valid, normalized,
consistently defined, and traceable to a documented source.

Because the framework's equations are deterministic pure functions — no machine
learning, no heuristics, no approximation — the integrity of the output is
entirely a function of the integrity of the inputs. A score is only as
trustworthy as the data that produced it. This document makes that dependency
explicit and provides a governance model that organizations can adopt to ensure
their scores are defensible.

---

## 2. Scope

**In scope:**

- The eleven raw metric inputs accepted by the framework: CR, ES, BT, RG, NCB,
  CS, BR, CA, SS, NCB_consumer, and T
- The normalization requirement ([0, 100] range for all raw metrics)
- The time normalization factor (T) and its semantics
- Input sourcing, validation, and traceability requirements
- The backlash terms (NCB, NCB_consumer) and their special governance status

**Out of scope:**

- The mathematical equations themselves (immutable; defined in `metrics.py`)
- Weight configuration (covered in `CALIBRATION.md`)
- Deployment infrastructure and API access controls (covered in `SECURITY.md`)
- Dashboard UI behavior

---

## 3. Context

The Goodwill KPI Framework accepts inputs through two channels:

1. **The HTTP API** (`/api/goodwill/calculate`, `/api/goodwill/export`): accepts
   a JSON payload with all eleven metric inputs and optional weight overrides.
2. **Direct Python invocation**: calls to `compute_G`, `compute_CG`, and
   `compute_UGS` from application code.

In both cases, the framework enforces range constraints on all metric inputs at
the point of calculation. However, constraint enforcement alone does not
constitute input governance. A value of `CR = 82` is technically valid whether
it represents last quarter's verified customer retention rate or an arbitrary
estimate. Governance determines which of those two interpretations is
acceptable in a given deployment context.

The backlash terms — NCB and NCB_consumer — carry special weight. They are
applied as first-class destructive forces: they reduce the goodwill score
directly and without clamping. A poorly sourced or inflated backlash value
will produce a score that systematically understates organizational health.
Conversely, a suppressed backlash value will produce an overstated score.
Both failures undermine the credibility of the measurement program.

---

## 4. Methodology / Approach

### Input Definitions

The following table defines each input, its role in the equations, and its
normalization requirement:

| Input | Full Name | Equation(s) | Range | Normalization Basis |
|---|---|---|---|---|
| CR | Customer Retention | G | [0, 100] | Percentage of customers retained over the observation window |
| ES | Employee Satisfaction | G | [0, 100] | Aggregated score from standardized employee survey |
| BT | Brand Trust | G | [0, 100] | Composite brand trust index from consumer research |
| RG | Revenue Growth | G | [0, 100] | Normalized revenue growth rate relative to a defined baseline |
| NCB | Net Customer Backlash | G | [0, 100] | Composite measure of complaints, churn signals, and negative sentiment |
| CS | Customer Satisfaction | CG | [0, 100] | Aggregated score from standardized customer satisfaction survey |
| BR | Brand Reputation | CG | [0, 100] | Composite brand reputation index from external or internal research |
| CA | Customer Advocacy | CG | [0, 100] | Net Promoter Score or equivalent advocacy measure, normalized |
| SS | Service Speed | CG | [0, 100] | Normalized service delivery speed relative to a defined benchmark |
| NCB_consumer | Negative Consumer Backlash | CG | [0, 100] | Composite measure of consumer complaints, returns, and negative reviews |
| T | Time Normalization Factor | G, UGS | > 0 | Length of the observation window in consistent units (e.g., quarters) |

### Normalization Requirements

All inputs except T must be normalized to the closed interval [0, 100] before
being submitted to the framework. The framework does not perform normalization;
it validates that the constraint is satisfied and raises a `ValueError` if it
is not.

Normalization must be:

- **Consistent across time periods.** The same normalization method must be
  applied to the same input in every observation window. Changing the
  normalization method for any input is equivalent to changing the effective
  weight of that input and constitutes a calibration change.

- **Documented.** The normalization formula for each input must be documented
  and version-controlled. Auditors must be able to reconstruct any normalized
  value from the raw source data.

- **Source-linked.** Each normalized value must be traceable to a named data
  source (e.g., a specific survey instrument, a data system, a report).

### Backlash Governance

NCB and NCB_consumer require heightened governance because their impact is
unconditional and asymmetric: a high backlash value can drive a score negative
regardless of how well other inputs are performing. The following controls are
recommended:

1. **Define backlash explicitly.** Document exactly what events, signals, or
   data sources contribute to NCB and NCB_consumer. Ambiguity in backlash
   definition is the single most common source of score manipulation risk.

2. **Source backlash from multiple independent signals.** A backlash measure
   derived from a single data source (e.g., only NPS detractors) is more
   susceptible to gaming than one that aggregates complaints, churn signals,
   return rates, and negative sentiment independently.

3. **Apply backlash at the observed value, never estimate it downward.** If
   backlash is uncertain, use the higher bound. The framework's design intent
   is honest accounting: backlash suppression produces misleading scores.

4. **Review backlash values before each reporting cycle.** Backlash is more
   sensitive to current events than other inputs. It warrants explicit review
   by a designated data steward before each submission.

### Time Factor Governance

T is the time normalization factor applied to G and UGS. It must be:

- **Explicitly set** for every calculation. The framework never infers T from
  wall-clock time.
- **Consistent within a time series.** If quarterly windows are used, T must
  remain equal to the number of quarters in the observation window across all
  calculations in the series.
- **Documented.** The unit and length of the observation window must be recorded
  alongside every score.

Changes to T — for example, switching from quarterly to monthly windows —
produce scores on a different scale and are not directly comparable to prior
scores. Such changes must be treated as a time-series discontinuity.

---

## 5. Governance Considerations

### Traceability

Every input submitted to the framework must be traceable to:

1. A named data source
2. A documented normalization formula
3. The date and period of the underlying measurement
4. The identity of the data steward who prepared or reviewed the value

This traceability chain is required for audit purposes and for reproducing any
score from archival data.

### Data Stewardship

Each input should be assigned a named data steward — a person or team
responsible for the accuracy and timeliness of that input's source data. Data
stewards are accountable for:

- Sourcing the raw data from the designated system of record
- Applying the documented normalization formula
- Reviewing the normalized value for reasonableness before submission
- Flagging anomalies for review before the value is included in a calculation

### Input Change Management

Any change to the definition, source, or normalization formula of any input must
go through a documented change management process equivalent to a calibration
change. Input definition changes affect score interpretation even when the
equations and weights are unchanged.

### Rejection of Invalid Inputs

The framework raises a `ValueError` for any input outside [0, 100] or any T ≤ 0.
These errors must be treated as data quality failures, not as calculation errors.
The responsible data steward must investigate the source of the invalid value
and correct it before resubmission. Invalid values must not be silently replaced
with boundary values (e.g., clamping 105 to 100) without governance approval
and documentation.

---

## 6. Operational Guidance

1. **Establish and document normalization formulas for all inputs before the
   first production calculation.** Normalization formulas that are defined
   retroactively are a governance gap.

2. **Assign a data steward to each input.** Do not allow inputs to be submitted
   without a designated owner who has reviewed the value.

3. **Store input records alongside output records.** Every score archive must
   include the full input vector and the T value used. The export file format
   produced by `/api/goodwill/export` satisfies this requirement for individual
   calculations.

4. **Treat backlash inputs as high-risk.** Apply the most rigorous sourcing and
   review controls to NCB and NCB_consumer. Consider requiring two-person
   approval before submitting backlash values to a production calculation.

5. **Flag and document any period where an input source is unavailable.** If
   a data source is temporarily unavailable, do not substitute estimated or
   interpolated values without governance approval. Document the gap.

6. **Do not compare scores across different T values without adjustment.**
   Scores computed with T = 1 are not on the same scale as scores computed
   with T = 4. Document T in every distributed score report.

7. **Conduct a pre-cycle input review.** Before each reporting cycle, the
   data steward team should review all inputs for completeness, anomalies,
   and consistency with prior periods. Anomalies should be investigated and
   resolved before scores are computed.

---

## 7. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Inconsistent normalization across time periods invalidating trend analysis | Medium | High | Document normalization formulas; treat formula changes as calibration changes |
| Backlash values suppressed to improve scores | Medium | High | Source backlash from multiple independent signals; apply two-person review; document all backlash values |
| Invalid inputs silently clamped to boundary values | Medium | Medium | Treat framework `ValueError` as data quality failures; require documented justification for any clamping |
| T value changed without documentation, breaking time-series comparability | Low | High | Document T in all score reports; treat T changes as time-series discontinuities |
| Input sourced from an unofficial or unreliable data system | Medium | High | Designate a system of record for each input; require data steward sign-off before submission |
| Missing backlash data estimated at zero | Low | High | Zero-backlash submissions require explicit data steward attestation that no backlash was observed |
| Anomalous input values (e.g., sudden spike in NCB) not investigated | Medium | Medium | Pre-cycle input review process; data stewards responsible for flagging anomalies |

---

## 8. Summary

The Goodwill KPI Framework is only as trustworthy as the inputs it receives.
The equations are deterministic and immutable; score integrity depends entirely
on the rigor of the input preparation process. This document defines the
governance model that transforms raw organizational data into the validated,
normalized, traceable inputs required by the framework.

The key principles are: every input must have a documented source and
normalization formula, a named data steward, and a pre-submission review.
Backlash inputs warrant heightened controls because of their direct, uncapped
impact on scores. T must be explicit, consistent, and documented in every score
report.

Organizations that follow this governance model can present their goodwill
scores to internal and external stakeholders with confidence that the scores
are defensible, reproducible, and free from silent manipulation.
