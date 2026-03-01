# ROADMAP.md — Goodwill KPI Framework

---

## 1. Purpose

This document describes the strategic direction of the Goodwill KPI Framework.
It communicates what the system is, what it is designed to remain, and what
categories of enhancement are conceptually consistent with its design
philosophy — without committing to specific timelines, without introducing new
dependencies, and without proposing changes to the implemented system.

The framework is complete and deployed. This document is not a backlog or a
release plan. It is a governance artifact that defines the boundaries within
which future evolution is considered philosophically sound, and the boundaries
beyond which proposed changes would alter the framework's fundamental character.

---

## 2. Scope

**In scope:**

- The strategic design philosophy of the framework
- Categories of enhancement that are conceptually consistent with the existing
  architecture
- Categories of change that are out of scope and would alter the framework's
  fundamental character
- Principles that should govern any future evolution

**Out of scope:**

- Specific implementation plans, timelines, or version targets
- Changes to `goodwill/metrics.py` (the equations are immutable)
- Changes to the API routes, dashboard, or repository structure
- New dependencies, new architectural components, or new infrastructure requirements

---

## 3. Context

The Goodwill KPI Framework was designed around four foundational commitments:

1. **Determinism.** Given identical inputs and weight configuration, the system
   produces identical outputs. No randomness, no approximation, no model drift.

2. **Auditability.** Every score is fully traceable to its inputs. No hidden
   state, no server-side computation that is not directly derivable from the
   request.

3. **Transparency.** The equations, weights, and term breakdowns are exposed
   directly to consumers. There are no black boxes.

4. **Operational realism.** The framework models backlash as a first-class
   destructive force. Scores can be negative. The system does not artificially
   constrain outputs to comfortable ranges.

Any future evolution of the framework must preserve all four of these
commitments. A proposed change that compromises any one of them is
inconsistent with the framework's design philosophy.

---

## 4. Methodology / Approach

### What the Framework Is

The Goodwill KPI Framework is a **calculation layer**, not an analytics
platform. It accepts normalized inputs, applies documented equations with
configurable weights, and returns auditable results. It does not store data,
generate forecasts, optimize weights, or make recommendations. This scope
boundary is intentional.

### Design Philosophy for Future Evolution

Future evolution should extend the framework's reach without adding complexity
to its core. Acceptable directions are those that:

- Add new output formats or integrations without changing the calculation layer
- Add documentation, governance guidance, or operational tooling without
  changing the application
- Improve observability or auditability without adding server-side state
- Extend the weight configuration surface without modifying the equations

Unacceptable directions are those that:

- Introduce machine learning, statistical modeling, or probabilistic scoring
  into the calculation layer
- Add server-side state, persistence, or caching
- Replace the weight-configurable model with a data-fitted model
- Introduce approximation or non-determinism anywhere in the calculation path
- Add authentication, user management, or access control to the calculation
  layer (these remain infrastructure-layer concerns)

### Conceptually Consistent Enhancements

The following enhancements are conceptually consistent with the framework's
design philosophy. They are described at the concept level only; no implementation
is proposed.

**1. Additional export formats.** The export endpoint currently supports xlsx
and csv. Additional formats — JSON-LD for linked data consumers, Parquet for
analytics pipelines, or signed PDF for compliance archives — would extend the
framework's reach without altering its calculation layer.

**2. Batch calculation endpoint.** A POST endpoint that accepts an array of
input vectors and returns an array of results would enable efficient
multi-period score computation without any change to the underlying equations.
Each element in the batch would be computed independently, preserving the
stateless, request-isolated character of the current design.

**3. Extended equation variants.** Organizations may require goodwill
equations adapted to specific sectors — public sector, nonprofit, healthcare —
where the relevant components differ from the current G and CG definitions.
Additional equation variants could be implemented as new pure functions
alongside the existing ones, without modifying or replacing them.

**4. Time-series score visualization.** The current dashboard displays a single
calculation. A visualization layer that accepts a time-ordered series of
archived calculation results and renders trend lines for G, CG, and UGS would
substantially increase the operational value of the framework for longitudinal
analysis. This visualization would be purely presentational; no new server-side
state would be introduced.

**5. Calculation verification endpoint.** An endpoint that accepts two
calculation records and returns a deterministic comparison — verifying that the
results are identical given the same inputs and weights — would formalize the
reproducibility verification practice described in `OBSERVABILITY.md`. This is
a documentation and governance tool, not a new computational capability.

**6. Weight configuration validation endpoint.** An endpoint that accepts a
proposed weight configuration, validates it against documented constraints
(e.g., weights sum to 1.0 within each equation), and returns a structured
validation report would support the calibration governance process described
in `CALIBRATION.md` without modifying the calculation layer.

---

## 5. Governance Considerations

### Immutability of the Core Equations

The three goodwill equations in `goodwill/metrics.py` are the intellectual
foundation of the framework. They have been validated, tested, and published.
Any change to these equations would require re-validation of all historical
scores, re-documentation of the mathematical basis, and governance approval
from the framework's author.

Proposals to modify the equations are out of scope for this roadmap and must
not be treated as routine enhancement requests.

### Backward Compatibility

Any future enhancement must preserve backward compatibility with the current
API contract. Existing consumers of `/api/goodwill/calculate` and
`/api/goodwill/export` must continue to function without modification. New
capabilities must be additive, not substitutive.

### Governance of Enhancements

Any change to the deployed system — including the addition of new endpoints or
new export formats — requires:

- A documented rationale aligned with the framework's design philosophy
- A review of the change's impact on the framework's four foundational
  commitments (determinism, auditability, transparency, operational realism)
- Approval by the framework's maintainer
- An update to the relevant documentation files before deployment

### Version Management

The framework currently operates at version 1.0.0. Any future release must
follow semantic versioning:

- **Patch** versions for documentation updates, bug fixes, and dependency
  security updates that do not alter API behavior.
- **Minor** versions for additive, backward-compatible new capabilities.
- **Major** versions for any change that alters the API contract, the equation
  behavior, or the weight configuration model.

---

## 6. Operational Guidance

1. **Treat this document as a governance constraint, not a feature queue.**
   The framework is complete. This document defines what future evolution
   is acceptable — it is not a commitment to implement any specific enhancement.

2. **Evaluate all enhancement proposals against the four foundational
   commitments.** A proposal that cannot be evaluated as deterministic,
   auditable, transparent, and operationally realistic is inconsistent with
   the framework's design philosophy.

3. **Do not modify `goodwill/metrics.py` under any circumstances.** The
   equations are immutable. Sector-specific or custom equation variants
   should be implemented as additional pure functions in a new module, not
   as modifications to the existing functions.

4. **Treat the API contract as a published interface.** Changes to request or
   response schemas require a minor or major version increment and advance
   notice to all consumers.

5. **Prioritize documentation and governance tooling over new computational
   features.** The framework's value is in its auditability and transparency.
   Enhancements that improve governance tooling (calibration support,
   observability, input validation) are more consistent with the framework's
   purpose than enhancements that add computational sophistication.

---

## 7. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Pressure to add machine learning or predictive scoring to the framework | Medium | High | Enforce the determinism commitment; document it explicitly as an out-of-scope direction |
| Enhancement proposals that modify core equations without governance review | Low | High | Document the immutability of `metrics.py`; require explicit approval for any change to that file |
| Backward-incompatible API changes introduced without version increment | Low | High | Enforce semantic versioning; require consumer impact assessment before any API change |
| Scope creep introducing server-side state or persistence | Low | High | Evaluate all proposals against the statelessness requirement; reject proposals that require state introduction |
| Documentation allowed to fall out of sync with implementation | Medium | Medium | Treat documentation updates as required components of any enhancement, not optional follow-on work |
| Enhancement prioritization driven by requests rather than design alignment | Medium | Medium | Use this document as the authoritative filter for evaluating enhancement proposals |

---

## 8. Summary

The Goodwill KPI Framework is complete. Its strategic direction is conservative
by design: preserve the four foundational commitments — determinism, auditability,
transparency, and operational realism — while extending reach through additive,
backward-compatible enhancements that do not alter the calculation layer.

The equations are immutable. The API contract is stable. The stateless
architecture is not subject to change. Future evolution, if any, will be
additive, documented, and governance-reviewed. This roadmap exists not to
promise new capabilities, but to define the principled boundaries within which
the framework can evolve without compromising the properties that make it
trustworthy.

---

## 9. Repository Tree Update

The following shows the updated repository tree with `ROADMAP.md` added at the
root. No existing files are modified.

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
├── conftest.py
├── CALIBRATION.md
├── CITATION.cff
├── INPUT-GOVERNANCE.md
├── LICENSE
├── OBSERVABILITY.md
├── README.md
├── ROADMAP.md                  ← new file
├── SECURITY.md
├── VALIDATION.md
├── render.yaml
├── requirements-dev.txt
└── requirements.txt
```
