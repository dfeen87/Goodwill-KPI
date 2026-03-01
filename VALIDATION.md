# Goodwill KPI Framework — Validation Report

> **Purpose:** This document simulates realistic organizational data through the
> Goodwill KPI Framework and validates that the three core equations produce
> correct, auditable, and meaningful results. Each simulation is accompanied by
> a step-by-step formula trace so that any stakeholder can reproduce the output
> independently.

---

## Table of Contents

1. [Mission of the Software](#1-mission-of-the-software)
2. [Why It Works — Design Principles](#2-why-it-works--design-principles)
3. [Mathematical Foundations](#3-mathematical-foundations)
4. [Default Weight Configuration](#4-default-weight-configuration)
5. [Simulated Scenarios](#5-simulated-scenarios)
   - [Scenario 1 — Thriving Retail Chain](#scenario-1--thriving-retail-chain)
   - [Scenario 2 — Recovering Nonprofit After Scandal](#scenario-2--recovering-nonprofit-after-scandal)
   - [Scenario 3 — Tech Startup: Revenue Surge with Viral Backlash](#scenario-3--tech-startup-revenue-surge-with-viral-backlash)
   - [Scenario 4 — Established Regional Bank, Long Observation Window](#scenario-4--established-regional-bank-long-observation-window)
   - [Scenario 5 — Systemic Crisis: Negative Goodwill](#scenario-5--systemic-crisis-negative-goodwill)
   - [Scenario 6 — Brand-Trust-Weighted Configuration](#scenario-6--brand-trust-weighted-configuration)
6. [Sensitivity Analyses](#6-sensitivity-analyses)
   - [NCB (Backlash) Sensitivity](#ncb-backlash-sensitivity)
   - [Time Window (T) Sensitivity](#time-window-t-sensitivity)
7. [Determinism and Auditability Verification](#7-determinism-and-auditability-verification)
8. [Interpretation Guide](#8-interpretation-guide)
9. [Anti-Patterns — What Not to Do](#9-anti-patterns--what-not-to-do)
10. [Validation Summary](#10-validation-summary)

---

## 1. Mission of the Software

Goodwill—the intangible value arising from relationships, reputation, and
trust—has historically been treated as an abstract accounting concept locked
inside balance sheets and resistant to real-time measurement. The **Goodwill KPI
Framework** exists to change that.

### Core Mission

> **Make organizational and consumer goodwill a first-class, measurable,
> auditable, and operationally actionable signal.**

The framework achieves this through three goals:

| Goal | How It Is Achieved |
|------|--------------------|
| **Quantify goodwill continuously** | Three deterministic equations convert observable metrics into numeric scores that can be tracked over time |
| **Expose the cost of backlash** | Net Customer Backlash (NCB) is a first-class destructive term—it can drive any score negative, enforcing honest accounting |
| **Enable governance-grade auditability** | Every score is fully traceable to its inputs; no hidden state, no server-side persistence, no client-side computation |

### Who Uses It

- **Executives** use the Unified Goodwill Score (UGS) to track organizational
  health across time.
- **Marketing and CX teams** use Consumer Goodwill (CG) to measure live
  customer-sentiment snapshots.
- **HR and Culture teams** use the Employee Satisfaction component of General
  Goodwill (G) to understand the workforce contribution to brand capital.
- **Compliance and audit teams** use the read-only dashboard and export
  capability to produce tamper-evident, reproducible reports.

---

## 2. Why It Works — Design Principles

### 2.1 Pure, Deterministic Functions

Every computation is a **pure function**: given identical inputs the output is
always identical, regardless of when, where, or how many times it is called.
There is no randomness, no database state, and no server-side caching that could
alter results between calls. This property is the bedrock of audit reliability.

```
f(inputs) → score   ← always the same score for the same inputs
```

### 2.2 Explicit Time Normalization

The time parameter `T` is **never inferred from a wall clock**. It must be
passed explicitly by the caller, and it must be documented. This design
prevents a silent class of errors where longer observation windows appear to
produce better scores simply because the denominator is larger, without the
analyst being aware.

A score of `G = 15.9` over `T = 4` quarters means something very different
from `G = 15.9` over `T = 1` quarter. The framework forces that context to be
explicit.

### 2.3 Backlash as a First-Class Destructive Force

Most KPI frameworks clamp negative sentiment at zero, producing misleadingly
optimistic scores. The Goodwill KPI Framework deliberately rejects this
practice. The `NCB` and `NCB_consumer` terms are **subtracted without
clamping**, meaning:

- An organization that retains customers and grows revenue can still record a
  *negative* goodwill score if backlash is sufficiently severe.
- This is not a flaw; it is an honest signal. A crisis that destroys brand
  trust produces a negative score, which is the correct information for
  decision-makers to have.

### 2.4 Read-Only Governance Dashboard

The HTTP dashboard never persists state and never executes logic on the client.
All inputs are submitted to the server, all computations run in the pure Python
functions, and all results are returned to the caller. This architecture ensures
that any score displayed in the UI can be independently reproduced by anyone
with the same inputs and the same open-source codebase.

### 2.5 Configurable Weights Without Code Changes

Default weights of `0.25` across all four components reflect equal prioritisation.
Any organization can override these via environment variables—without touching
the source code—to reflect their strategic priorities. Every deviation from
defaults is documented in the `weights_used` block of every API response,
creating a self-describing audit trail.

---

## 3. Mathematical Foundations

### Equation 1 — General Goodwill (G)

Measures **time-averaged organizational goodwill** across four internal
performance dimensions, penalised by net customer backlash.

```
G = ((CR·w₁) + (ES·w₂) + (BT·w₃) + (RG·wₜ) − NCB) / T
```

| Symbol | Metric | Range | Default Weight |
|--------|--------|-------|---------------|
| CR | Customer Retention | [0, 100] | w₁ = 0.25 |
| ES | Employee Satisfaction | [0, 100] | w₂ = 0.25 |
| BT | Brand Trust | [0, 100] | w₃ = 0.25 |
| RG | Revenue Growth | [0, 100] | wₜ = 0.25 |
| NCB | Net Customer Backlash | [0, 100] | (destructive) |
| T | Time normalization factor | T > 0 | (explicit) |

**Key property:** G **may be negative** when NCB exceeds the weighted sum.

---

### Equation 2 — Consumer Goodwill (CG)

Measures **instantaneous consumer sentiment** across four customer-facing
dimensions, penalised by negative consumer backlash. Intentionally not
time-normalised.

```
CG = (CS·w₁) + (BR·w₂) + (CA·w₃) + (SS·w₄) − NCB_consumer
```

| Symbol | Metric | Range | Default Weight |
|--------|--------|-------|---------------|
| CS | Customer Satisfaction | [0, 100] | w₁ = 0.25 |
| BR | Brand Reputation | [0, 100] | w₂ = 0.25 |
| CA | Customer Advocacy | [0, 100] | w₃ = 0.25 |
| SS | Service Speed | [0, 100] | w₄ = 0.25 |
| NCB_consumer | Negative Consumer Backlash | [0, 100] | (destructive) |

**Key property:** CG is a snapshot. It does **not** change simply because T
is larger; this makes it suitable for point-in-time comparisons.

---

### Equation 3 — Unified Goodwill Score (UGS)

Combines G and CG into a single aggregate score, normalised over the observation
window.

```
UGS = ((G·w₁) + (CG·w₂)) / T
```

| Symbol | Source | Default Weight |
|--------|--------|---------------|
| G | Output of Equation 1 | w₁ = 0.5 |
| CG | Output of Equation 2 | w₂ = 0.5 |
| T | Same T used for G | (explicit) |

---

## 4. Default Weight Configuration

All simulations in this report use the framework defaults unless otherwise
stated.

| Parameter | Environment Variable | Default Value | Applied To |
|-----------|---------------------|---------------|-----------|
| g_w1 | `GOODWILL_G_W1` | 0.25 | CR in G equation |
| g_w2 | `GOODWILL_G_W2` | 0.25 | ES in G equation |
| g_w3 | `GOODWILL_G_W3` | 0.25 | BT in G equation |
| g_w_t | `GOODWILL_G_W_T` | 0.25 | RG in G equation |
| cg_w1 | `GOODWILL_CG_W1` | 0.25 | CS in CG equation |
| cg_w2 | `GOODWILL_CG_W2` | 0.25 | BR in CG equation |
| cg_w3 | `GOODWILL_CG_W3` | 0.25 | CA in CG equation |
| cg_w4 | `GOODWILL_CG_W4` | 0.25 | SS in CG equation |
| ugs_w1 | `GOODWILL_UGS_W1` | 0.50 | G in UGS equation |
| ugs_w2 | `GOODWILL_UGS_W2` | 0.50 | CG in UGS equation |

Equal weights across G's four components means every dimension of
organizational performance is treated as equally important by default.
This is an explicit governance decision, not a shortcut.

---

## 5. Simulated Scenarios

Each scenario presents:

1. A realistic organizational context
2. The raw metric inputs
3. A full step-by-step formula trace
4. The computed output values (displayed to 4 decimal places; full IEEE 754
   double precision is used internally and results are reproducible exactly)
5. An interpretation of what the numbers mean

---

### Scenario 1 — Thriving Retail Chain

**Context:** A national retail chain with strong customer loyalty, healthy
employee morale, and consistent revenue growth over four quarters. Backlash is
minimal — occasional complaints managed within SLA.

#### Input Data

| Metric | Value | Meaning |
|--------|-------|---------|
| CR (Customer Retention) | 88 | 88 % of customers return |
| ES (Employee Satisfaction) | 82 | Strong workforce morale |
| BT (Brand Trust) | 85 | High market credibility |
| RG (Revenue Growth) | 78 | Solid 4-quarter growth |
| NCB (Net Customer Backlash) | 5 | Minimal negative sentiment |
| **T (Time Factor)** | **4** | **4 quarters** |
| CS (Customer Satisfaction) | 91 | Post-purchase survey score |
| BR (Brand Reputation) | 87 | NPS and media sentiment |
| CA (Customer Advocacy) | 76 | Referral and review activity |
| SS (Service Speed) | 83 | Fulfilment and support SLAs met |
| NCB_consumer | 4 | Very low live backlash |

#### Formula Trace

**Step 1 — General Goodwill (G):**
```
G = ((CR·0.25) + (ES·0.25) + (BT·0.25) + (RG·0.25) − NCB) / T
  = ((88·0.25) + (82·0.25) + (85·0.25) + (78·0.25) − 5) / 4
  = (22.00 + 20.50 + 21.25 + 19.50 − 5) / 4
  = 78.25 / 4
  = 19.5625
```

**Step 2 — Consumer Goodwill (CG):**
```
CG = (CS·0.25) + (BR·0.25) + (CA·0.25) + (SS·0.25) − NCB_consumer
   = (91·0.25) + (87·0.25) + (76·0.25) + (83·0.25) − 4
   = 22.75 + 21.75 + 19.00 + 20.75 − 4
   = 80.25
```

**Step 3 — Unified Goodwill Score (UGS):**
```
UGS = ((G·0.5) + (CG·0.5)) / T
    = ((19.5625·0.5) + (80.25·0.5)) / 4
    = (9.78125 + 40.125) / 4
    = 49.90625 / 4
    = 12.4766
```

#### Results

| Score | Value | Interpretation |
|-------|-------|---------------|
| **G** | **19.5625** | Healthy time-averaged organizational goodwill |
| **CG** | **80.2500** | Excellent instantaneous consumer sentiment |
| **UGS** | **12.4766** | Positive aggregate after 4-quarter normalization |

**Interpretation:** The high CG (80.25) reflects the excellent customer
experience snapshot. G is naturally lower because it is divided by `T = 4`,
reflecting that performance has been distributed across four quarters rather
than concentrated in one burst. UGS combines both and normalises again — a
stable, positive result indicating a well-governed, consumer-trusted
organization.

---

### Scenario 2 — Recovering Nonprofit After Scandal

**Context:** A nonprofit discovered a financial mismanagement incident 9 months
ago. Leadership has been replaced and transparency initiatives are underway.
The organization is 3 months into recovery (T = 1 quarter observed). Employee
satisfaction is cautiously recovering; public trust is rebuilding slowly.

#### Input Data

| Metric | Value | Meaning |
|--------|-------|---------|
| CR | 55 | Donor/member retention dropped ~30 % |
| ES | 60 | Staff confidence cautiously returning |
| BT | 40 | Brand trust heavily damaged |
| RG | 20 | Revenue streams disrupted |
| NCB | 35 | Ongoing negative coverage and complaints |
| **T** | **1** | **Single quarter** (recovery phase) |
| CS | 58 | Service recipients report mixed experience |
| BR | 42 | Reputation still recovering |
| CA | 35 | Few advocates; most staying silent |
| SS | 65 | Service delivery remained consistent |
| NCB_consumer | 30 | Continued public dissatisfaction |

#### Formula Trace

**Step 1 — G:**
```
G = ((55·0.25) + (60·0.25) + (40·0.25) + (20·0.25) − 35) / 1
  = (13.75 + 15.00 + 10.00 + 5.00 − 35) / 1
  = 43.75 − 35
  = 8.75
```

**Step 2 — CG:**
```
CG = (58·0.25) + (42·0.25) + (35·0.25) + (65·0.25) − 30
   = 14.50 + 10.50 + 8.75 + 16.25 − 30
   = 50.00 − 30
   = 20.00
```

**Step 3 — UGS:**
```
UGS = ((8.75·0.5) + (20.00·0.5)) / 1
    = (4.375 + 10.00) / 1
    = 14.375
```

#### Results

| Score | Value | Interpretation |
|-------|-------|---------------|
| **G** | **8.7500** | Low but positive — recovery is real, not illusory |
| **CG** | **20.0000** | Consumer sentiment is depressed but above zero |
| **UGS** | **14.3750** | Positive signal; organization is on the right side of zero |

**Interpretation:** The scores are low, but they are **honest**. The NCB of 35
correctly punishes the score for ongoing public consequences of the scandal.
Critically, the organization is still **above zero**, which reflects that
service delivery (SS = 65) and cautious staff recovery (ES = 60) are providing
genuine, if modest, goodwill signals. Tracking these scores across quarters will
produce a trend line that documents the recovery — or reveals a stall.

---

### Scenario 3 — Tech Startup: Revenue Surge with Viral Backlash

**Context:** A fast-growing consumer tech startup recorded a record revenue
quarter. However, a data privacy controversy went viral on social media at the
same time. Engagement metrics remain strong but trust and brand reputation have
collapsed. Revenue growth looks excellent; goodwill does not.

#### Input Data

| Metric | Value | Meaning |
|--------|-------|---------|
| CR | 72 | Retention still okay — product is sticky |
| ES | 68 | Employees feel uncertain; morale dipping |
| BT | 30 | Brand Trust severely damaged by controversy |
| RG | 90 | Best revenue quarter on record |
| NCB | 75 | Massive wave of public criticism |
| **T** | **1** | **Single quarter** |
| CS | 65 | Customers still use product but are unhappy |
| BR | 25 | Brand Reputation near-collapse in media |
| CA | 40 | Advocacy dropped dramatically |
| SS | 80 | App performance unaffected |
| NCB_consumer | 80 | Viral backlash, boycott calls |

#### Formula Trace

**Step 1 — G:**
```
G = ((72·0.25) + (68·0.25) + (30·0.25) + (90·0.25) − 75) / 1
  = (18.00 + 17.00 + 7.50 + 22.50 − 75) / 1
  = 65.00 − 75
  = −10.00
```

**Step 2 — CG:**
```
CG = (65·0.25) + (25·0.25) + (40·0.25) + (80·0.25) − 80
   = 16.25 + 6.25 + 10.00 + 20.00 − 80
   = 52.50 − 80
   = −27.50
```

**Step 3 — UGS:**
```
UGS = ((−10.00·0.5) + (−27.50·0.5)) / 1
    = (−5.00 + (−13.75)) / 1
    = −18.75
```

#### Results

| Score | Value | Interpretation |
|-------|-------|---------------|
| **G** | **−10.0000** | ⚠ Negative — backlash exceeds weighted performance |
| **CG** | **−27.5000** | ⚠ Strongly negative consumer sentiment |
| **UGS** | **−18.7500** | ⚠ Organisation is in a goodwill deficit |

**Interpretation:** This scenario demonstrates the most important capability of
the framework: **revenue growth cannot hide a goodwill crisis**. Despite
`RG = 90` — a perfect-quarter revenue figure — the backlash of 75 produces a
negative G and strongly negative CG. A traditional financial KPI dashboard
would show a great quarter. The Goodwill KPI Framework shows the truth: the
organization is spending down intangible capital faster than it is earning it,
and no amount of revenue growth compensates for that in this model.

---

### Scenario 4 — Established Regional Bank, Long Observation Window

**Context:** A regional bank that has operated for decades with consistent,
if unspectacular, performance. The 12-quarter observation window (T = 12)
reflects a 3-year strategic review cycle. Consumer experience is high-quality
and stable; revenue growth is modest.

#### Input Data

| Metric | Value | Meaning |
|--------|-------|---------|
| CR | 80 | Strong long-term customer relationships |
| ES | 74 | Solid but not exceptional staff morale |
| BT | 79 | Trust built over decades |
| RG | 45 | Slow, steady growth — conservative industry |
| NCB | 8 | Very low ongoing complaints |
| **T** | **12** | **12 quarters (3-year review)** |
| CS | 77 | Satisfaction scores in line with industry |
| BR | 80 | Strong brand reputation |
| CA | 68 | Good but not exceptional advocacy |
| SS | 60 | Service is reliable; not fastest |
| NCB_consumer | 6 | Minimal sustained backlash |

#### Formula Trace

**Step 1 — G:**
```
G = ((80·0.25) + (74·0.25) + (79·0.25) + (45·0.25) − 8) / 12
  = (20.00 + 18.50 + 19.75 + 11.25 − 8) / 12
  = 61.50 / 12
  = 5.1250
```

**Step 2 — CG:**
```
CG = (77·0.25) + (80·0.25) + (68·0.25) + (60·0.25) − 6
   = 19.25 + 20.00 + 17.00 + 15.00 − 6
   = 71.25 − 6
   = 65.25
```

**Step 3 — UGS:**
```
UGS = ((5.125·0.5) + (65.25·0.5)) / 12
    = (2.5625 + 32.625) / 12
    = 35.1875 / 12
    = 2.9323
```

#### Results

| Score | Value | Interpretation |
|-------|-------|---------------|
| **G** | **5.1250** | Low G due to long window — consistent, not spectacular |
| **CG** | **65.2500** | Good instantaneous consumer sentiment |
| **UGS** | **2.9323** | Low UGS due to double T normalisation |

**Interpretation:** The low G and UGS scores are **not a bad sign** — they
reflect the mathematics of a long observation window. The key insight is that
CG = 65.25 is a healthy consumer sentiment snapshot, independent of T.
Comparing this bank's G score to Scenario 1's G score (19.56) without
accounting for the difference in T (`T=12` vs `T=4`) would be a serious
analytical error — exactly the kind the framework is designed to prevent by
requiring T to be explicit and documented.

---

### Scenario 5 — Systemic Crisis: Negative Goodwill

**Context:** A utility company experiencing a simultaneous internal and
external crisis: a major service outage, whistleblower complaints about
workplace conditions, and a coordinated social media campaign. All metrics
have collapsed; backlash is near-maximum.

#### Input Data

| Metric | Value | Meaning |
|--------|-------|---------|
| CR | 30 | Mass customer defections underway |
| ES | 25 | Staff morale near breakdown |
| BT | 15 | Brand trust near-zero |
| RG | 10 | Revenue contracting |
| NCB | 90 | Severe sustained backlash |
| **T** | **1** | **Single quarter** |
| CS | 20 | Customers deeply dissatisfied |
| BR | 10 | Brand reputation catastrophically damaged |
| CA | 15 | Almost no advocacy |
| SS | 30 | Service failures ongoing |
| NCB_consumer | 95 | Near-maximum consumer backlash |

#### Formula Trace

**Step 1 — G:**
```
G = ((30·0.25) + (25·0.25) + (15·0.25) + (10·0.25) − 90) / 1
  = (7.50 + 6.25 + 3.75 + 2.50 − 90) / 1
  = 20.00 − 90
  = −70.00
```

**Step 2 — CG:**
```
CG = (20·0.25) + (10·0.25) + (15·0.25) + (30·0.25) − 95
   = 5.00 + 2.50 + 3.75 + 7.50 − 95
   = 18.75 − 95
   = −76.25
```

**Step 3 — UGS:**
```
UGS = ((−70.00·0.5) + (−76.25·0.5)) / 1
    = (−35.00 + (−38.125)) / 1
    = −73.125
```

#### Results

| Score | Value | Interpretation |
|-------|-------|---------------|
| **G** | **−70.0000** | ⛔ Severe negative organizational goodwill |
| **CG** | **−76.2500** | ⛔ Catastrophic consumer sentiment |
| **UGS** | **−73.1250** | ⛔ Organisation is deeply in goodwill deficit |

**Interpretation:** This is the framework's **crisis signal**. There is nothing
ambiguous about a UGS of −73. The backlash terms dominate every dimension of
performance. This score would, over successive quarters, trace the depth and
duration of the crisis — and eventually show whether recovery interventions
are moving the needle. The negative scores are the correct and informative
output; a framework that clamped scores at zero would hide the severity
entirely and deprive decision-makers of the signal they need.

---

### Scenario 6 — Brand-Trust-Weighted Configuration

**Context:** A luxury goods company for which brand trust and brand reputation
are strategic crown jewels — far more important than service speed or immediate
revenue. The organization has configured custom weights to reflect this
priority.

#### Input Data

| Metric | Value | Meaning |
|--------|-------|---------|
| CR | 75 | Good retention |
| ES | 70 | Solid employee satisfaction |
| BT | 95 | Exceptional brand trust (core asset) |
| RG | 65 | Good revenue growth |
| NCB | 10 | Very low backlash |
| **T** | **2** | **2 quarters** |
| CS | 80 | High customer satisfaction |
| BR | 95 | Outstanding brand reputation (core asset) |
| CA | 72 | Good advocacy |
| SS | 68 | Acceptable service speed |
| NCB_consumer | 8 | Very low consumer backlash |

#### Custom Weight Configuration

| Weight | Default | Custom | Applied To |
|--------|---------|--------|-----------|
| g_w1 | 0.25 | 0.15 | CR |
| g_w2 | 0.25 | 0.15 | ES |
| **g_w3** | **0.25** | **0.55** | **BT (brand trust emphasised)** |
| g_w_t | 0.25 | 0.15 | RG |
| cg_w1 | 0.25 | 0.15 | CS |
| **cg_w2** | **0.25** | **0.55** | **BR (brand reputation emphasised)** |
| cg_w3 | 0.25 | 0.15 | CA |
| cg_w4 | 0.25 | 0.15 | SS |

#### Formula Trace — Custom Weights

**Step 1 — G (custom weights):**
```
G = ((75·0.15) + (70·0.15) + (95·0.55) + (65·0.15) − 10) / 2
  = (11.25 + 10.50 + 52.25 + 9.75 − 10) / 2
  = 73.75 / 2
  = 36.875
```

**Step 2 — CG (custom weights):**
```
CG = (80·0.15) + (95·0.55) + (72·0.15) + (68·0.15) − 8
   = 12.00 + 52.25 + 10.80 + 10.20 − 8
   = 77.25
```

**Step 3 — UGS:**
```
UGS = ((36.875·0.5) + (77.25·0.5)) / 2
    = (18.4375 + 38.625) / 2
    = 57.0625 / 2
    = 28.5312
```

#### Comparison: Custom vs Default Weights

| Score | Default Weights | Custom Weights | Difference |
|-------|----------------|----------------|-----------|
| **G** | 33.1250 | 36.8750 | +3.75 |
| **CG** | 70.7500 | 77.2500 | +6.50 |
| **UGS** | 25.9688 | 28.5312 | +2.56 |

**Interpretation:** The custom weight configuration correctly amplifies the
already-excellent brand trust scores (BT = 95, BR = 95), producing higher
scores that accurately reflect the organization's strategic definition of
"goodwill". This is not score manipulation — it is strategic priority
alignment. The `weights_used` block in every API response documents exactly
which weights produced the score, making it impossible to compare a
custom-weighted score against a default-weighted score without awareness of
the difference.

---

## 6. Sensitivity Analyses

### NCB (Backlash) Sensitivity

**Setup:** All G-equation inputs fixed at 75 (equal, moderate performance).
T = 1 (single period). NCB varies from 0 to 100.

| NCB | G Score | Interpretation |
|-----|---------|---------------|
| 0 | 75.0000 | Perfect — no backlash |
| 10 | 65.0000 | Minor backlash; still healthy |
| 20 | 55.0000 | Moderate backlash; score reduced meaningfully |
| 30 | 45.0000 | Significant backlash; leadership attention required |
| 40 | 35.0000 | High backlash; crisis in development |
| 50 | 25.0000 | Critical threshold — backlash equals half performance |
| 60 | 15.0000 | Severe backlash; goodwill depleting rapidly |
| 70 | 5.0000 | Near-zero; one bad quarter away from negative |
| **80** | **−5.0000** | **⚠ Negative — backlash exceeds performance** |
| 90 | −15.0000 | Deep deficit; structural intervention needed |
| 100 | −25.0000 | Maximum backlash against average performance |

**Key finding:** With uniform metric scores of 75, NCB crosses the zero
threshold at NCB = 75 (the exact weighted sum). This is not a coincidence — it
is the mathematical tipping point. Any organization with NCB > weighted_sum is
in a goodwill deficit regardless of how strong its other metrics are.

---

### Time Window (T) Sensitivity

**Setup:** Fixed input data (CR=80, ES=75, BT=78, RG=70, NCB=12). CG held at
65.0 for UGS calculation. T varies from 1 to 12 quarters.

| T (quarters) | G Score | UGS Score | Interpretation |
|-------------|---------|-----------|---------------|
| 1 | 63.7500 | 64.375 | Single quarter — full signal |
| 2 | 31.8750 | 24.219 | 2-quarter average — score halved |
| 4 | 15.9375 | 10.117 | Annual review — signal quartered |
| 6 | 10.6250 | 6.302 | 18-month window |
| 8 | 7.9688 | 4.561 | 2-year window |
| 12 | 5.3125 | 2.930 | 3-year strategic review |

**Key finding:** G and UGS both decrease monotonically as T increases — this
is correct behaviour. A high G score over T = 1 does not represent the same
sustained performance as a high G over T = 12. The framework forces this to
be explicit rather than presenting a single number without context. When
comparing scores across organizations or time periods, T must always be
identical for the comparison to be meaningful.

---

## 7. Determinism and Auditability Verification

A central guarantee of the framework is that the same inputs always produce
the same outputs, regardless of how many times the computation is executed.

### Test: 5 Identical Calls

**Inputs:** CR=75, ES=80, BT=70, RG=85, NCB=15, T=3

| Call # | G Result |
|--------|---------|
| 1 | 20.833333333333332 |
| 2 | 20.833333333333332 |
| 3 | 20.833333333333332 |
| 4 | 20.833333333333332 |
| 5 | 20.833333333333332 |

**All 5 calls identical:** ✅ `True`

This is verified both at the Python function level and at the HTTP API level
— the `/api/goodwill/calculate` endpoint returns identical JSON for identical
request bodies.

### Manual Verification

Any result in this document can be independently verified by:

1. **Using the API directly:**
   ```bash
   curl -X POST http://localhost:8000/api/goodwill/calculate \
     -H "Content-Type: application/json" \
     -d '{
       "CR": 88, "ES": 82, "BT": 85, "RG": 78, "NCB": 5,
       "CS": 91, "BR": 87, "CA": 76, "SS": 83, "NCB_consumer": 4,
       "T": 4
     }'
   ```

2. **Using the Python functions directly:**
   ```python
   from goodwill.metrics import compute_G, compute_CG, compute_UGS

   G   = compute_G(CR=88, ES=82, BT=85, RG=78, NCB=5, T=4)
   CG  = compute_CG(CS=91, BR=87, CA=76, SS=83, NCB_consumer=4)
   UGS = compute_UGS(G=G, CG=CG, T=4)
   print(G, CG, UGS)  # 19.5625  80.25  12.476562...
   ```

3. **By arithmetic** using the formula traces in Section 5 above.

All three approaches will yield identical results.

---

## 8. Interpretation Guide

### Score Context

Goodwill scores are meaningful only in context. The following table provides
general reference bands for equal-weight configurations with T = 1:

| G (T=1) | CG | UGS (T=1) | Condition |
|---------|----|-----------|-----------|
| > 50 | > 50 | > 50 | **Excellent** — strong goodwill with low backlash |
| 20 – 50 | 30 – 60 | 20 – 50 | **Healthy** — positive net goodwill |
| 5 – 20 | 10 – 30 | 5 – 20 | **Fragile** — needs attention, trend is key |
| 0 – 5 | 0 – 10 | 0 – 5 | **At Risk** — approaching goodwill deficit |
| < 0 | < 0 | < 0 | **Crisis** — backlash exceeds total positive goodwill |

> **Important:** These bands are illustrative only. They shift with T and with
> custom weights. Always compare like-for-like (same T, same weights).

### Trend Analysis Is Essential

A single score tells you where you are. A sequence of scores tells you where
you are going. The framework is designed to support trend analysis by:

- Enforcing explicit T so that quarter-over-quarter comparisons are consistent
- Returning all input terms in the API response so anomalies can be traced
- Never smoothing or caching results, so each measurement is an independent
  data point

### The CG–G Gap

The gap between G and CG is often more informative than either score alone:

| Pattern | Meaning |
|---------|---------|
| CG >> G | Consumers are happy but organizational fundamentals are weak — unsustainable |
| G >> CG | Internal performance is strong but consumers are dissatisfied — experience gap |
| Both high | Aligned goodwill — internal and external signals agree |
| Both negative | Systemic crisis — internal and external problems are co-occurring |

---

## 9. Anti-Patterns — What Not to Do

The framework documentation and test suite explicitly warn against the
following practices.

### ❌ Comparing Scores With Different T Values

```
# WRONG — not a valid comparison
Organisation A: G = 15.9  (T = 4)
Organisation B: G = 63.7  (T = 1)
```

These scores come from the same underlying metric data (see Section 6). They
are not comparable. Divide by T before comparing, or ensure both use the same
T.

### ❌ Clamping Backlash to Zero

```
# WRONG — hides the crisis signal
G = max(0, compute_G(CR, ES, BT, RG, NCB=90, T=1))
```

Clamping the NCB input or the output at zero destroys the most important
information in the model. Scenario 3 and 5 above would both show G = 0
with clamping — hiding completely different situations (one is a backlash
crisis atop strong revenue; the other is a total organizational collapse).

### ❌ Inferring T Automatically

```
# WRONG — creates hidden context dependency
T = (datetime.now() - measurement_start).days / 90
G = compute_G(..., T=T)
```

T must be a deliberate, documented business decision, not a wall-clock
calculation. If T changes silently, historical scores become incomparable.

### ❌ Using Scores as Optimisation Targets

The framework measures goodwill; it does not optimise it. Gaming the inputs
(e.g., reporting artificially high ES to boost G) destroys the informational
value of the system. These are measurement tools, not incentive mechanisms.

---

## 10. Validation Summary

| Test | Result |
|------|--------|
| **Formula correctness — all 6 scenarios** | ✅ All computed values verified by hand |
| **Determinism — 5 identical calls** | ✅ Identical output every time |
| **Negative scores — Scenarios 3 and 5** | ✅ Backlash correctly drives scores below zero |
| **Time normalisation effect** | ✅ Scores scale inversely with T as designed |
| **NCB sensitivity** | ✅ Linear, unclamped, crosses zero at weighted-sum threshold |
| **Custom weight configuration** | ✅ Deviations from default correctly amplify priority dimensions |
| **CG invariance over T** | ✅ CG does not change when T changes (instantaneous by design) |
| **Weight documentation** | ✅ All API responses include `weights_used` block |

All scenarios in this document were computed using the live Python functions
in `goodwill/metrics.py` with default weights from `goodwill/config.py`. The
formula traces in Section 5 reproduce the Python results by hand to the full
precision of the expressions.

The Goodwill KPI Framework correctly quantifies organizational and consumer
goodwill as deterministic, auditable, time-aware, and backlash-sensitive
metrics — delivering on its core mission of making goodwill a first-class
operational signal.

---

*Generated against commit on branch `copilot/simulate-goodwill-kpi-metrics`.
All numeric values are reproducible with `python -c "from goodwill.metrics import compute_G, compute_CG, compute_UGS; ..."` using the functions in this repository.*
