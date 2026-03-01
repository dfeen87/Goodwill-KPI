# OBSERVABILITY.md — Goodwill KPI Framework

---

## 1. Purpose

This document defines the observability model for the Goodwill KPI Framework.
Observability encompasses the practices, instrumentation points, and operational
signals that allow teams to understand the runtime behavior of the system, detect
anomalies, verify correctness of calculations, and maintain confidence in the
integrity of the scores produced over time.

Because the framework is stateless and its equations are deterministic, its
observability needs differ from those of a stateful application. The primary
concerns are not data consistency or transaction integrity, but rather input
quality over time, score trend analysis, deployment health, and the ability
to reconstruct any calculation from its constituent parts.

---

## 2. Scope

**In scope:**

- API endpoint health and availability signals
- Score output monitoring and trend analysis patterns
- Input quality observation over time
- Export artifact traceability
- Deployment-level observability signals (process health, configuration)
- Calculation reproducibility verification

**Out of scope:**

- Modifications to the application code to add instrumentation (the system is
  complete as deployed)
- Third-party APM or observability platform integrations (these are
  infrastructure-layer decisions)
- Authentication or access audit logging (covered in `SECURITY.md`)
- Input governance controls (covered in `INPUT-GOVERNANCE.md`)

---

## 3. Context

The Goodwill KPI Framework is a stateless HTTP service. It does not maintain
a database, a cache, or any in-process state between requests. Every response
is deterministically derived from the request payload and the weight
configuration in effect at process startup.

This architecture has important observability implications:

- **There is no internal state to monitor.** All observability signals come
  from the HTTP layer (request/response), the process layer (health, startup),
  and the application layer (weight configuration at startup).

- **Score correctness is verifiable by replaying inputs.** Because the equations
  are pure functions, any score can be independently recomputed from its input
  vector and weight configuration. This is the primary mechanism for verifying
  calculation integrity.

- **Score trends require external time-series storage.** The framework does not
  persist scores. Longitudinal analysis requires that scores and their input
  vectors be archived by the consuming system or operator.

The dashboard at `/dashboard` provides a human-readable view of individual
calculations. The export endpoint at `/api/goodwill/export` provides structured
data suitable for archival and downstream analysis.

---

## 4. Methodology / Approach

### Layer 1 — Process Health

The `/health` endpoint returns `{"status": "ok"}` with HTTP 200 when the
application is running and the weight configuration has loaded successfully.
A non-200 response from `/health` indicates a startup failure, which is most
commonly caused by an invalid `GOODWILL_*` environment variable.

Health check behavior:

| Condition | `/health` response | Interpretation |
|---|---|---|
| Service running normally | `200 {"status": "ok"}` | All weight configuration loaded; service ready |
| Invalid environment variable at startup | Process fails to start | `config.py` raises `ValueError` before the app starts |
| Process crashed after startup | No response / connection refused | Restart required |

Health checks should be configured at the infrastructure layer (Render.com,
load balancer, or container orchestrator) to poll `/health` at regular intervals.
Any failure should trigger an alert and, if configured, an automatic restart.

### Layer 2 — API Observability

The four API routes produce observable signals at the HTTP layer:

| Route | Observable Signals |
|---|---|
| `GET /health` | Response time, status code |
| `GET /dashboard` | Response time, status code, HTML response size |
| `POST /api/goodwill/calculate` | Response time, status code, response payload |
| `POST /api/goodwill/export` | Response time, status code, file size |

Recommended observability instrumentation at the infrastructure layer:

- **Request rate** per endpoint
- **Error rate** (4xx for invalid inputs, 5xx for unexpected failures)
- **Response latency** (p50, p95, p99)
- **Payload size** for calculate and export responses

A `422 Unprocessable Entity` response from `/api/goodwill/calculate` indicates
an input validation failure. These should be monitored because a sustained rate
of 422 errors may indicate a misconfigured client or a data quality issue in
the input preparation pipeline.

### Layer 3 — Score Output Monitoring

Because the framework does not persist scores, score output monitoring requires
that consuming systems or operators archive calculation results. The recommended
approach is to archive the full JSON response from `/api/goodwill/calculate`,
which includes:

- All three final scores (G, CG, UGS)
- All term breakdowns (G_terms, CG_terms, UGS_terms)
- The exact weights used (`weights_used`)
- The full input vector (recoverable from `G_terms`, `CG_terms`, and the
  top-level inputs)

With this archive, the following score observability practices are possible:

**Trend monitoring:** Plot G, CG, and UGS over time to detect sustained
upward or downward trends, sudden score changes, and anomalous single-period
deviations.

**Input contribution analysis:** Compare term breakdowns across periods to
identify which components are driving score changes. A score decrease driven
entirely by an NCB spike has a different operational interpretation than one
driven by declining CR.

**Backlash surveillance:** Track NCB and NCB_consumer over time independently.
Because these terms have a disproportionate impact on scores, early detection
of rising backlash is operationally valuable.

**Weight configuration audit:** The `weights_used` field in every response
enables automated detection of weight configuration changes. If the weights
in a response differ from those in previous responses, a weight change occurred
and should be investigated.

### Layer 4 — Export Artifact Traceability

The `/api/goodwill/export` endpoint produces a timestamped file
(`goodwill_export_{timestamp}.{format}`) containing the full calculation record.
These files serve as point-in-time audit artifacts.

For governance purposes, export files should be archived with:

- The ISO 8601 timestamp embedded in the filename
- The identity of the requester (if captured at the infrastructure layer)
- The observation period the inputs represent (recorded externally, as the
  framework does not accept period metadata)

### Layer 5 — Calculation Reproducibility Verification

Any score can be verified by replaying the original input vector through the
equations with the original weights. This verification can be performed:

1. **Via the API:** Resubmit the original JSON payload to
   `/api/goodwill/calculate`. The result must match the original response
   exactly.

2. **Via direct Python invocation:** Call `compute_G`, `compute_CG`, and
   `compute_UGS` directly with the original inputs and weights. Results must
   match to floating-point precision.

3. **By hand calculation:** Apply the documented formulas to the input values
   and weights. For scores that are distributed to stakeholders, hand
   verification of at least one score per reporting cycle is recommended.

---

## 5. Governance Considerations

### Auditability of Score History

The framework itself does not maintain a score history. The responsibility for
maintaining an auditable score history rests with the operator. The minimum
required archive for each reporting cycle is:

- The full input vector for each calculation
- The weight configuration in effect (captured in `weights_used`)
- The final scores (G, CG, UGS)
- The observation period the inputs represent
- The date and time of the calculation

Export files produced by `/api/goodwill/export` satisfy the first four
requirements. The observation period must be recorded externally.

### Score Anomaly Review Process

When score monitoring detects an anomaly — a sudden change, an out-of-range
value, or an unexpected trend — the following review process should be followed:

1. Retrieve the full input vector for the anomalous period.
2. Verify that inputs are within the valid [0, 100] range and are sourced
   from the designated data systems (per `INPUT-GOVERNANCE.md`).
3. Check whether the weight configuration changed between the anomalous period
   and the prior period.
4. Recompute the score via the API to verify that the archived score matches
   the recomputed score (confirming no calculation error).
5. If the anomaly is confirmed as data-driven, escalate to the relevant data
   steward for investigation of the underlying source data.

### Configuration Drift Detection

If the deployment platform does not alert on environment variable changes,
configuration drift can be detected by comparing the `weights_used` field in
successive calculation responses. Any change in `weights_used` that was not
preceded by a documented weight change decision is a configuration governance
failure and requires immediate investigation.

---

## 6. Operational Guidance

1. **Configure infrastructure-level health checks on `/health` with a polling
   interval appropriate to the deployment SLA.** A non-200 response requires
   immediate investigation.

2. **Archive the full JSON response from every `/api/goodwill/calculate` call
   that represents a production reporting cycle.** This is the foundation of
   score observability.

3. **Monitor the 422 error rate on `/api/goodwill/calculate`.** A sustained
   rate of 422 errors indicates input data quality issues that require
   investigation by the data steward team.

4. **Plot G, CG, and UGS over time on a consistent T basis.** Trend
   visualization is the primary operational tool for detecting goodwill
   deterioration before it reaches crisis levels.

5. **Track NCB and NCB_consumer independently.** Because backlash terms are
   first-class destructive forces, early warning signals in backlash data are
   more actionable than lagging composite score signals.

6. **Verify score reproducibility at least once per reporting cycle.** Replay
   the previous cycle's inputs through the API and confirm that the result
   matches the archived score. This verifies that the weight configuration
   has not changed unexpectedly.

7. **Record the observation period alongside every archived score.** The
   framework does not accept period metadata; it must be recorded by the
   operator. Without period metadata, a score archive cannot support trend
   analysis.

---

## 7. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Score history not archived, preventing trend analysis | Medium | High | Establish archival procedures before the first production calculation cycle |
| Weight configuration change undetected, invalidating trend comparisons | Low | High | Monitor `weights_used` field across successive calculations; treat changes as configuration governance events |
| Sustained 422 error rate indicating input quality failure not investigated | Medium | Medium | Alert on 422 error rate threshold; route alerts to data steward team |
| Health check failures not triggering alerts | Low | High | Configure infrastructure-layer health monitoring on `/health` before production deployment |
| Score anomaly investigated without full input vector available | Medium | High | Archive full input vectors (or export files) for all production calculations |
| Export file timestamps not preserved, preventing period reconstruction | Low | Medium | Archive export files with original filenames; record observation period metadata externally |
| Calculation reproducibility not verified, masking undetected weight drift | Low | Medium | Include reproducibility verification in each reporting cycle's pre-publication checklist |

---

## 8. Summary

The Goodwill KPI Framework's stateless, deterministic architecture makes it
inherently observable at the calculation level: any score can be reproduced and
verified from its inputs at any time. What it does not provide is longitudinal
observability — that must be constructed by the operator through archival of
calculation results and infrastructure-level monitoring of the API.

The key observability practices are: health-check the process, archive every
production calculation result, monitor input quality through 422 error rates,
track score trends over time with consistent T values, and verify score
reproducibility on each reporting cycle. These practices, applied consistently,
give operators and governance stakeholders confidence that the scores they
receive are correct, stable, and free from undetected configuration drift.

---

## 9. Repository Tree Update

The following shows the updated repository tree with `OBSERVABILITY.md` added
at the root. No existing files are modified.

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
