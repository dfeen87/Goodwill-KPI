# Goodwill Quantification Framework

## Purpose

This module implements three deterministic, governance-grade equations for
measuring organizational and consumer goodwill as auditable KPIs.

---

## Equations

### 1. General Goodwill (G)

```
G = ((CR·w1) + (ES·w2) + (BT·w3) + (RG·w(t)) − NCB) / T
```

| Symbol | Meaning                  | Range    |
|--------|--------------------------|----------|
| CR     | Customer Retention       | [0, 100] |
| ES     | Employee Satisfaction    | [0, 100] |
| BT     | Brand Trust              | [0, 100] |
| RG     | Revenue Growth           | [0, 100] |
| w1–w3  | Static weights           | —        |
| w(t)   | Time-dependent weight for RG | —    |
| NCB    | Net Customer Backlash    | [0, 100] |
| T      | Time normalization factor | T > 0   |

**Interpretation:** Time-averaged organizational goodwill over a measurement
window of length T.  A higher T dilutes the instantaneous score across a
longer observation window.

---

### 2. Consumer Goodwill (CG)

```
CG = (CS·w1) + (BR·w2) + (CA·w3) + (SS·w4) − NCB_consumer
```

| Symbol       | Meaning                     | Range    |
|--------------|-----------------------------|----------|
| CS           | Customer Satisfaction       | [0, 100] |
| BR           | Brand Reputation            | [0, 100] |
| CA           | Customer Advocacy           | [0, 100] |
| SS           | Service Speed               | [0, 100] |
| NCB_consumer | Negative Consumer Backlash  | [0, 100] |

**Interpretation:** Instantaneous consumer sentiment state.  **No time
normalization is applied by design.**  This is a snapshot, not an average.

---

### 3. Unified Goodwill Score (UGS)

```
UGS = ((G·w1) + (CG·w2)) / T
```

| Symbol | Meaning                        |
|--------|--------------------------------|
| G      | General Goodwill (see above)   |
| CG     | Consumer Goodwill (see above)  |
| T      | Time normalization factor (T > 0) |

**Interpretation:** A single score combining organizational and consumer
goodwill dimensions, normalized over time T for longitudinal consistency.

**Assumption:** G and CG must be on compatible scales before aggregation.
The caller is responsible for this normalization.

---

## Assumptions

1. All raw metric inputs are normalized to **[0, 100]** before being passed
   to any function.  Inputs outside this range raise a `ValueError`.
2. `T` is always passed **explicitly**.  It is never inferred from wall-clock
   time.  It represents the length of the observation window in a consistent
   unit (e.g., quarters, months).
3. Backlash terms (NCB, NCB_consumer) are **first-class destructive forces**.
   They are not clamped or softened.  A large backlash value will yield a
   lower or negative goodwill score; this is the correct behavior.
4. All weights are dimensionless scalars with sensible equal-weighting
   defaults.  They can be overridden via environment variables (see
   `config.py`) or passed directly as keyword arguments.

---

## Weight Configuration

Weights can be set via environment variables at process startup:

| Variable              | Default | Applies to |
|-----------------------|---------|------------|
| `GOODWILL_G_W1`       | 0.25    | CR in G    |
| `GOODWILL_G_W2`       | 0.25    | ES in G    |
| `GOODWILL_G_W3`       | 0.25    | BT in G    |
| `GOODWILL_G_W_T`      | 0.25    | RG in G    |
| `GOODWILL_CG_W1`      | 0.25    | CS in CG   |
| `GOODWILL_CG_W2`      | 0.25    | BR in CG   |
| `GOODWILL_CG_W3`      | 0.25    | CA in CG   |
| `GOODWILL_CG_W4`      | 0.25    | SS in CG   |
| `GOODWILL_UGS_W1`     | 0.5     | G in UGS   |
| `GOODWILL_UGS_W2`     | 0.5     | CG in UGS  |

---

## Warnings

- **Do not interpret a single score in isolation.**  Goodwill scores are
  meaningful only in trend context across comparable time windows.
- **Do not compare scores across organizations** without verifying that the
  same weight configuration and normalization methodology were used.
- **Do not suppress the backlash terms.**  Clamping NCB or NCB_consumer
  will produce misleadingly optimistic scores that mask systemic issues.
- **Do not infer T from calendar time automatically.**  T must be a
  deliberate, documented choice tied to a governance review cycle.
- **These equations are measurement tools, not optimization targets.**
  Gaming individual metrics to inflate the score defeats the purpose.

---

## Usage

```python
from goodwill.metrics import compute_G, compute_CG, compute_UGS

G = compute_G(CR=85, ES=78, BT=80, RG=70, NCB=5, T=4)
CG = compute_CG(CS=88, BR=82, CA=75, SS=72, NCB_consumer=8)
UGS = compute_UGS(G=G, CG=CG, T=4)
```
