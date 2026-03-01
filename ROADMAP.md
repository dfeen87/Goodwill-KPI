# ROADMAP

## Purpose

This document describes the forward-looking roadmap for the Goodwill-KPI project.  
Its purpose is to make explicit which enhancements are planned, which are intentionally out of scope, and how future work will preserve the deterministic, auditable nature of the core goodwill equations.

The roadmap is descriptive, not prescriptive: it outlines likely directions and priorities while keeping the current implementation stable, reproducible, and safe to adopt in production environments.

---

## Scope

This roadmap covers:

- **Optional, non-core enhancements** to:
  - Security and deployment posture
  - Calibration methodology and statistical rigor
  - Input governance and normalization standards
  - Observability and production operations
  - Dashboard UX and stakeholder usability
- **Documentation and governance artifacts** that clarify how Goodwill-KPI should be used and interpreted.
- **Versioning and release philosophy** for the project.

This roadmap explicitly does **not** cover:

- Changes to the core goodwill equations in `goodwill/metrics.py`
- Fundamental shifts in the project’s purpose (e.g., becoming a financial valuation engine)
- Turning the project into a multi-tenant SaaS product or user account system
- Any feature that would introduce persistent state or side-effectful business logic into the core library

The core equations and their deterministic implementation are considered stable and foundational.

---

## Context

Goodwill-KPI provides:

- A set of **pure, deterministic equations** for:
  - General Goodwill (G)
  - Consumer Goodwill (CG)
  - Unified Goodwill Score (UGS)
- A **read-only FastAPI dashboard** for executing and visualizing these equations
- A **Python package** suitable for integration into existing systems
- A **VALIDATION.md** file documenting simulations and statistical checks

The roadmap builds on this foundation by:

- Improving **governance readiness** (security posture, input standards, calibration guidance)
- Enhancing **operational readiness** (observability, deployment clarity)
- Increasing **stakeholder usability** (dashboard UX, interpretability aids)
- Maintaining strict separation between:
  - Core math (`goodwill/metrics.py`)
  - Configuration (`goodwill/config.py`)
  - API and dashboard (`app/`)
  - Documentation and governance artifacts (`*.md`)

All future work must respect this separation.

---

## Methodology / Approach

Future development will follow these principles:

1. **Core math is immutable**  
   The equations and their implementation in `goodwill/metrics.py` are treated as a stable reference. Any future work assumes these functions are correct, deterministic, and not subject to refactoring for feature reasons.

2. **Optional layers, not mandatory complexity**  
   Enhancements are layered on top of the existing system as **optional modules, configurations, or documents**, not as required dependencies. A minimal deployment should remain as simple as:
   - Install dependencies
   - Run the FastAPI app
   - Use the dashboard or API

3. **Documentation-first for governance features**  
   For security, calibration, input governance, and observability, the first step is always **clear documentation**:
   - What is recommended
   - What is optional
   - What is out of scope
   Only then, where appropriate, small, well-bounded implementation hooks may be added.

4. **No hidden state, no opaque behavior**  
   Any future feature must preserve:
   - Determinism of calculations
   - Traceability from outputs back to inputs and weights
   - Clear, inspectable configuration via environment variables or explicit parameters

5. **Versioned, incremental evolution**  
   Changes will be grouped into minor and patch releases, with clear release notes and no breaking changes to the public API without a major version bump.

---

## Governance considerations

The roadmap is designed to support:

- **Auditability**  
  Organizations should be able to:
  - Reproduce any score from inputs and configuration
  - Understand how weights and inputs were chosen
  - Document calibration decisions and normalization standards

- **Compliance posture**  
  While Goodwill-KPI does not process highly sensitive data by default, the roadmap anticipates:
  - Clear deployment guidance (e.g., private vs. public endpoints)
  - Optional access controls and rate limiting
  - Logging and metrics that support internal governance and incident review

- **Methodological transparency**  
  Calibration, normalization, and interpretation guidance will be:
  - Explicit
  - Documented
  - Separable from the core equations
  This avoids “black box” behavior while allowing organizations to adapt the framework to their context.

- **Boundary clarity**  
  The roadmap will continue to emphasize what Goodwill-KPI is **not**:
  - Not a financial valuation engine
  - Not a replacement for accounting goodwill
  - Not a sentiment classifier or data collection system
  - Not a multi-tenant SaaS platform

---

## Operational guidance

This section outlines the main roadmap themes and how they are expected to be applied in real deployments.

### 1. Security and deployment posture (optional hardening)

Planned direction:

- **SECURITY.md** documenting:
  - Recommended deployment patterns (e.g., behind an API gateway, private network, or VPN)
  - Optional API key or token-based protection at the FastAPI layer
  - Optional rate limiting at the reverse proxy or gateway level
- Clear statement that:
  - The core library is safe to embed in internal systems
  - The public exposure of the demo dashboard/API should be controlled by the deployer

Operationally, teams can:

- Deploy the app internally without auth for low-risk use cases
- Add API gateway-level auth and rate limiting for external or multi-team access
- Use SECURITY.md as a reference for internal security reviews

### 2. Calibration methodology and statistical rigor

Planned direction:

- **CALIBRATION.md** describing:
  - How to choose and document weights for different sectors or organizations
  - How to use historical data to calibrate weights (e.g., correlation with known outcomes)
  - How to maintain comparability across time and teams
- Optional examples:
  - Sector-specific weight presets (e.g., B2B SaaS, consumer retail, non-profit)
  - A conceptual workflow for calibration using notebooks (kept outside the core package)

Operationally, teams can:

- Start with equal weights (the default)
- Gradually introduce calibrated weights with documented rationale
- Use CALIBRATION.md as a governance artifact for internal review and sign-off

### 3. Input governance and normalization standards

Planned direction:

- **INPUT-GOVERNANCE.md** describing:
  - Required input range ([0, 100]) and why it matters
  - Recommended normalization pipelines (e.g., mapping survey scores, NPS, or internal indices)
  - Documentation expectations for each input (source, update frequency, owner)
- Optional helper patterns (documented, not enforced in code) for:
  - Handling missing data
  - Handling outliers
  - Ensuring consistency across teams and time periods

Operationally, teams can:

- Define internal data contracts for each input (CR, ES, BT, RG, CS, BR, CA, SS, NCB terms)
- Use INPUT-GOVERNANCE.md as a reference for data engineering and analytics teams
- Treat normalization decisions as part of their governance process, not as ad-hoc choices

### 4. Observability and production operations

Planned direction:

- **OBSERVABILITY.md** describing:
  - Recommended logging practices (e.g., structured logs with request IDs, input validation errors, calculation durations)
  - Optional metrics (e.g., request counts, error rates, latency) exposed via middleware or external tooling
  - Optional tracing hooks (e.g., OpenTelemetry) for organizations that already use distributed tracing

Operationally, teams can:

- Integrate Goodwill-KPI into existing logging and monitoring stacks
- Use OBSERVABILITY.md as a guide for:
  - What to log
  - How to interpret logs and metrics
  - How to support incident response and governance reporting

### 5. Dashboard UX and interpretability enhancements

Planned direction (all optional, read-only):

- Scenario quality-of-life improvements:
  - Local, browser-only saved scenarios (no server-side persistence)
  - Side-by-side scenario comparison views
- Interpretability aids:
  - Inline explanations of each term and its role
  - Guidance on interpreting negative goodwill or large NCB terms
- Visualization enhancements:
  - Contribution breakdown charts (e.g., bar or waterfall)
  - Time-series views when users supply time-indexed data

Operationally, teams can:

- Use the existing dashboard as-is for simple, read-only exploration
- Extend or fork the dashboard for richer internal tooling, while preserving the core equations
- Treat the dashboard as a reference implementation, not a mandated UI

---

## Risks & mitigations

### Risk 1: Scope creep into a full platform

**Description:**  
There is a risk that incremental enhancements (auth, UX, observability) could push the project toward becoming a full-fledged platform rather than a reference implementation.

**Mitigations:**

- Keep all enhancements **optional** and **non-invasive**
- Maintain a clear boundary between:
  - Core library
  - Example API/dashboard
  - Documentation
- Use ROADMAP.md to explicitly mark what is out of scope

---

### Risk 2: Misinterpretation as a financial valuation tool

**Description:**  
Users may misinterpret goodwill scores as financial valuations or accounting measures.

**Mitigations:**

- Continue to emphasize in README and documentation:
  - Scores are comparative indicators, not valuations
  - Intended use is trend analysis and strategic insight
- Add interpretability guidance in future documentation (e.g., CALIBRATION.md, INPUT-GOVERNANCE.md)

---

### Risk 3: Inconsistent calibration across teams

**Description:**  
Different teams may calibrate weights differently, leading to incomparable scores.

**Mitigations:**

- Provide a clear calibration methodology in CALIBRATION.md
- Encourage organizations to:
  - Document calibration decisions
  - Standardize presets across teams
- Emphasize that cross-team comparability requires shared calibration standards

---

### Risk 4: Poor input governance leading to misleading outputs

**Description:**  
If inputs are poorly normalized or inconsistently sourced, outputs may be misleading despite correct equations.

**Mitigations:**

- Provide explicit input governance guidance in INPUT-GOVERNANCE.md
- Encourage:
  - Data contracts
  - Source documentation
  - Regular review of input pipelines
- Treat input governance as a first-class part of the methodology

---

### Risk 5: Over-reliance on the dashboard

**Description:**  
Stakeholders may treat the demo dashboard as the primary or only interface, even when deeper integration is more appropriate.

**Mitigations:**

- Position the dashboard as:
  - A reference implementation
  - A read-only exploration tool
- Encourage production teams to:
  - Integrate the Python package directly
  - Build internal tooling around the core library

---

## Summary

The Goodwill-KPI roadmap focuses on **governance, clarity, and operational readiness** rather than expanding the project’s scope or complexity.

Key themes include:

- Optional security and deployment hardening
- Clear calibration methodology and documentation
- Strong input governance and normalization standards
- Practical observability guidance for production environments
- Incremental, read-only UX enhancements for the dashboard

Throughout all future work, the core principles remain:

- The equations are deterministic and immutable.
- The implementation is transparent and auditable.
- Enhancements are optional, layered, and non-invasive.
- The project remains a reference framework, not a monolithic platform.
