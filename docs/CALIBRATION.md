# CALIBRATION.md — Goodwill KPI Framework

---

## 1. Purpose

This document defines the calibration methodology for the Goodwill KPI
Framework. Calibration is the process of selecting, validating, and documenting
the weight values that govern how each raw metric contributes to the final
goodwill scores. Because the three goodwill equations are deterministic and
weight-configurable, the interpretive meaning of every score is directly
determined by the weight choices in effect at the time of calculation.

This document exists to ensure that weight configuration decisions are
deliberate, documented, and reproducible — not incidental — and that any
organization deploying the framework can defend its score interpretations to
internal and external stakeholders.

---

## 2. Scope

**In scope:**

- The weight parameters governing `compute_G`, `compute_CG`, and `compute_UGS`
- The environment variables that override default weights at deployment time
- The process of selecting, validating, and documenting weight choices
- Sensitivity analysis methodology for understanding weight impact
- Governance controls for weight change management

**Out of scope:**

- Modifications to the mathematical structure of the three equations (the
  equations are immutable)
- Normalization of raw source data to the [0, 100] input range (covered in
  `INPUT-GOVERNANCE.md`)
- Deployment infrastructure configuration
- The dashboard UI

---

## 3. Context

The Goodwill KPI Framework exposes three equations:

| Equation | Formula |
|---|---|
| General Goodwill (G) | `((CR·w1) + (ES·w2) + (BT·w3) + (RG·w(t)) − NCB) / T` |
| Consumer Goodwill (CG) | `(CS·w1) + (BR·w2) + (CA·w3) + (SS·w4) − NCB_consumer` |
| Unified Goodwill Score (UGS) | `((G·w1) + (CG·w2)) / T` |

Every weight is a dimensionless scalar applied to a normalized [0, 100] input.
The default configuration uses equal weighting within each equation (0.25 for
four-term equations, 0.5 for two-term equations). Equal weighting is a
principled default — it makes no assumption about organizational priorities —
but it is not the only valid configuration.

Calibration is the process of moving deliberately from default weights to
context-specific weights when the organization's measurement priorities warrant
it. All non-default weight configurations must be documented and treated as
governance artifacts.

---

## 4. Methodology / Approach

### Default Weight Configuration

The default weights, loaded from `goodwill/config.py` and overridable via
environment variables, are:

| Variable | Default | Applies To |
|---|---|---|
| `GOODWILL_G_W1` | `0.25` | CR (Customer Retention) in G |
| `GOODWILL_G_W2` | `0.25` | ES (Employee Satisfaction) in G |
| `GOODWILL_G_W3` | `0.25` | BT (Brand Trust) in G |
| `GOODWILL_G_W_T` | `0.25` | RG (Revenue Growth) in G |
| `GOODWILL_CG_W1` | `0.25` | CS (Customer Satisfaction) in CG |
| `GOODWILL_CG_W2` | `0.25` | BR (Brand Reputation) in CG |
| `GOODWILL_CG_W3` | `0.25` | CA (Customer Advocacy) in CG |
| `GOODWILL_CG_W4` | `0.25` | SS (Service Speed) in CG |
| `GOODWILL_UGS_W1` | `0.5` | G (General Goodwill) in UGS |
| `GOODWILL_UGS_W2` | `0.5` | CG (Consumer Goodwill) in UGS |

Equal weighting treats all components as equally important. This is appropriate
for first deployments, cross-sector benchmarking, and scenarios where no
empirical basis exists for differentiating component importance.

### Calibration Process

A structured calibration follows five steps:

1. **Establish the measurement objective.** Identify what the score is intended
   to capture. A customer-experience-focused deployment may weight CS and BR
   more heavily in CG. An employee-engagement-focused deployment may weight ES
   more heavily in G.

2. **Document the rationale for each weight.** Every weight that deviates from
   the default must have a written justification. Acceptable bases include
   empirical correlation data, domain expert consensus, regulatory requirements,
   or strategic priority alignment.

3. **Verify weight sum constraints.** The framework does not enforce that weights
   within an equation sum to any specific value. However, for scores to be
   interpretable on a consistent scale, the sum of weights within each equation
   should equal 1.0 (i.e., weights should sum to unity). Document explicitly
   if this constraint is intentionally relaxed.

4. **Run sensitivity analysis.** Before finalizing non-default weights, compute
   scores across the expected input range under the proposed weights and under
   the default weights. Verify that the score behavior is consistent with the
   intended measurement objective and that extreme weight choices do not produce
   degenerate outputs.

5. **Record the calibration decision.** Store the final weight values, their
   justifications, the date of adoption, and the name of the approving
   authority. This record is a governance artifact and should be version-controlled
   alongside the deployment configuration.

### Per-Request Weight Overrides

The `/api/goodwill/calculate` and `/api/goodwill/export` endpoints accept
optional per-request weight overrides in the JSON body (`g_w1`, `g_w2`,
`g_w3`, `g_w_t`, `cg_w1`, `cg_w2`, `cg_w3`, `cg_w4`, `ugs_w1`, `ugs_w2`).
Per-request overrides are intended for exploratory analysis and scenario
modeling. They do not modify the deployment-level weight configuration.

When per-request overrides are used, the `weights_used` field in the response
reflects the actual weights applied, enabling full auditability at the
calculation level.

### Sensitivity Analysis

To understand the impact of weight choices, compute G, CG, and UGS under:

- The proposed weight configuration
- The default equal-weight configuration
- A configuration where each weight is independently set to its minimum and
  maximum plausible values while other weights are held at default

Document the range of score variation across these configurations for a
representative set of inputs. If the range is narrow, the score is robust to
weight choices. If the range is wide, weight selection is material and must
be governed carefully.

The `VALIDATION.md` document in this repository contains worked numerical
examples across six scenarios that can serve as calibration reference points.

---

## 5. Governance Considerations

### Auditability of Weight Choices

Every calculation result returned by the API includes a `weights_used` field
that records the exact weights applied. Every export file includes the same
information. This means that any score, at any point in time, can be traced
to its exact weight configuration without relying on configuration management
records alone.

### Weight Change Management

Changes to deployment-level weights (i.e., changes to environment variables)
must follow a change management process that includes:

- A written justification for the change
- A before/after comparison of scores for a representative input set
- Approval by a designated weight governance authority (e.g., analytics
  leadership, a KPI governance committee)
- A record of the change date and the identity of the approving authority

Scores computed before a weight change are not directly comparable to scores
computed after. Time-series analyses must account for weight configuration
changes as discontinuities.

### Reproducibility

A score is reproducible if and only if the original inputs and the original
weights are both available. The export file format preserves both. Operators
who require long-term reproducibility must archive export files or the
equivalent input/weight records.

---

## 6. Operational Guidance

1. **Use the default weights for all first deployments.** Establish a baseline
   score history before introducing custom weights. This enables meaningful
   before/after comparison when weights are later adjusted.

2. **Document every non-default weight configuration.** Store weight
   configurations in version control alongside the deployment environment
   files. Treat weight configuration as code.

3. **Never change weights silently.** A weight change without documentation
   invalidates historical comparisons and undermines the auditability guarantee
   of the framework.

4. **Use per-request weight overrides for modeling, not for production
   reporting.** Production reporting must use the deployment-level weight
   configuration to ensure consistency across reports.

5. **Communicate weight configurations to score consumers.** Any stakeholder
   who receives goodwill scores must be informed of the weight configuration
   in effect. Scores produced under different weight configurations are not
   directly comparable.

6. **Re-run sensitivity analysis after any significant change to the input
   data collection methodology.** If the normalization approach for any input
   changes, the effective weight applied to that input changes even if the
   weight parameter itself does not.

---

## 7. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Undocumented weight changes invalidating historical comparisons | Medium | High | Require documented change management for all weight configuration changes |
| Weights summing to values other than 1.0, producing uninterpretable score scales | Medium | Medium | Validate weight sums before deployment; document intentional deviations |
| Calibration decisions made without empirical basis | Medium | Medium | Require written rationale for all non-default weights; treat calibration records as governance artifacts |
| Per-request weight overrides used in production reporting | Low | Medium | Restrict per-request overrides to exploratory use; production reports must reference deployment-level configuration |
| Score consumers unaware of weight configuration in effect | Medium | High | Include `weights_used` in all distributed score reports; document configuration in all reporting artifacts |
| Extreme weight values producing degenerate scores | Low | Medium | Conduct sensitivity analysis before finalizing non-default configurations |

---

## 8. Summary

Calibration is the governance process that determines what a goodwill score
means. The Goodwill KPI Framework provides flexible, environment-variable-
controlled weights with principled equal-weighting defaults. Any organization
deploying the framework with non-default weights must treat those weights as
governance artifacts: documented, justified, version-controlled, and communicated
to all score consumers.

The framework's architecture makes calibration auditable by design. Every score
includes the exact weights used to produce it. This makes score interpretation
traceable and defensible without relying on external documentation alone.

---

## 9. Repository Tree Update

The following shows the updated repository tree with `CALIBRATION.md` added at
the root. No existing files are modified.

```
Goodwill-KPI/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── templates/
│       └── dashboard.html
├── goodwill/
│   ├── __init__.py
│   ├── README.md
│   ├── config.py
│   └── metrics.py
├── tests/
│   ├── __init__.py
│   ├── test_dashboard.py
│   └── test_goodwill.py
├── docs/
│   ├── CALIBRATION.md
│   ├── CITATION.cff
│   ├── INPUT-GOVERNANCE.md
│   ├── LICENSE
│   ├── OBSERVABILITY.md
│   ├── ROADMAP.md
│   ├── SECURITY.md
│   └── VALIDATION.md
├── conftest.py
├── README.md
├── render.yaml
├── requirements-dev.txt
└── requirements.txt
```
