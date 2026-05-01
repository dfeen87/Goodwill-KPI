# Goodwill-KPI

[![CI](https://github.com/dfeen87/Goodwill-KPI/actions/workflows/ci.yml/badge.svg)](https://github.com/dfeen87/Goodwill-KPI/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org)

## What is this?

**Goodwill-KPI** is a deterministic, auditable framework for quantifying organizational and consumer goodwill as measurable key performance indicators (KPIs). It provides three pure mathematical equations — General Goodwill (G), Consumer Goodwill (CG), and a Unified Goodwill Score (UGS) — backed by a lightweight FastAPI dashboard that executes and visualizes the calculations in a browser.

## Why does it exist?

Goodwill is one of the most strategically important yet least rigorously measured assets an organization holds. Most existing approaches treat it as a subjective narrative or a residual accounting entry. Goodwill-KPI replaces intuition with a transparent, weight-configurable formula that can be tracked over time, exported for audit, and re-run deterministically from any set of inputs. Because all logic lives in pure functions with no side effects, the scores are fully reproducible and traceable to their inputs.

## Who is it for?

- **Strategy and operations teams** that want a structured, quantitative lens on brand health, employee experience, and customer sentiment without building custom analytics tooling.
- **Governance and compliance functions** that need auditable KPI calculations with documented assumptions and repeatable results.
- **Researchers and analysts** who want a reference implementation of goodwill quantification that can be extended, weight-tuned, or embedded in a larger data pipeline.
- **Developers** who want to self-host a read-only KPI dashboard or integrate the `goodwill` Python package directly into existing systems.

> ⚠ **Scores are comparative indicators, not financial valuations.** They are meaningful in trend context across comparable time windows, not as standalone absolute numbers.

---

## Repository Structure

```
Goodwill-KPI/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI pipeline (pytest on Python 3.11 & 3.12)
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application and API routes
│   └── templates/
│       └── dashboard.html      # Read-only browser dashboard
├── docs/
│   ├── CALIBRATION.md          # Calibration guidance and tuning notes
│   ├── INPUT-GOVERNANCE.md     # Input governance and data quality guidelines
│   ├── OBSERVABILITY.md        # Observability and monitoring notes
│   ├── ROADMAP.md              # Project roadmap
│   ├── SECURITY.md             # Security policy
│   └── VALIDATION.md           # Validation methodology and test coverage notes
├── goodwill/
│   ├── __init__.py
│   ├── README.md               # Detailed equation reference and usage guide
│   ├── config.py               # Weight defaults (env-var overridable)
│   └── metrics.py              # Pure functions: compute_G, compute_CG, compute_UGS
├── tests/
│   ├── __init__.py
│   ├── test_config.py          # Unit tests for weight configuration loading
│   ├── test_dashboard.py       # API and dashboard integration tests
│   └── test_goodwill.py        # Unit tests for all metric functions
├── CITATION.cff                # Citation metadata
├── conftest.py                 # Shared pytest fixtures
├── LICENSE                     # MIT License
├── render.yaml                 # Render.com deployment configuration
├── requirements-dev.txt        # Development dependencies (pytest, httpx, …)
└── requirements.txt            # Runtime dependencies (fastapi, uvicorn, …)
```

---

## Core Equations

| Equation | Formula | Notes |
|---|---|---|
| General Goodwill (G) | `((CR·w1)+(ES·w2)+(BT·w3)+(RG·w(t))−NCB) / T` | Time-normalized |
| Consumer Goodwill (CG) | `(CS·w1)+(BR·w2)+(CA·w3)+(SS·w4)−NCB_consumer` | Instantaneous |
| Unified Goodwill Score (UGS) | `((G·w1)+(CG·w2)) / T` | Time-normalized |

All inputs must be normalized to **[0, 100]** before being passed to the functions. Backlash terms (NCB, NCB_consumer) are first-class destructive forces and are never clamped.

See [`goodwill/README.md`](goodwill/README.md) for full symbol definitions, assumptions, and worked examples.

---

## Quick Start

### Python library

```python
from goodwill.metrics import compute_G, compute_CG, compute_UGS

G   = compute_G(CR=85, ES=78, BT=80, RG=70, NCB=5, T=4)
CG  = compute_CG(CS=88, BR=82, CA=75, SS=72, NCB_consumer=8)
UGS = compute_UGS(G=G, CG=CG, T=4)
```

### Dashboard (local)

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/dashboard` in a browser.

---

## API Routes

| Route | Method | Description |
|---|---|---|
| `/health` | GET | Liveness probe — returns `{"status": "ok"}` |
| `/dashboard` | GET | Read-only calculation interface (HTML) |
| `/api/goodwill/calculate` | POST | Accepts JSON inputs; returns G, CG, UGS and term breakdowns |
| `/api/goodwill/export` | POST | Returns a downloadable xlsx or csv of the full calculation |

All goodwill equations are executed **server-side** via the pure functions in `goodwill.metrics`. No state is stored or persisted. No client-side calculation is performed.

---

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

---

## Deployment (Render.com)

The repository includes a `render.yaml` that configures a **Render.com** web service.

1. Connect the repository to your Render account.
2. Render will automatically detect `render.yaml` and create the service.
3. The service binds to the port provided by Render via `$PORT`.

**Manual deployment steps (if YAML auto-deploy is not available):**

- Environment: Python
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## Configuration

All weights default to equal weighting and can be overridden at process startup via environment variables.

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8000` | HTTP port (set automatically by Render) |
| `GOODWILL_G_W1` | `0.25` | Weight for CR in G equation |
| `GOODWILL_G_W2` | `0.25` | Weight for ES in G equation |
| `GOODWILL_G_W3` | `0.25` | Weight for BT in G equation |
| `GOODWILL_G_W_T` | `0.25` | Time-dependent weight w(t) for RG in G equation |
| `GOODWILL_CG_W1` | `0.25` | Weight for CS in CG equation |
| `GOODWILL_CG_W2` | `0.25` | Weight for BR in CG equation |
| `GOODWILL_CG_W3` | `0.25` | Weight for CA in CG equation |
| `GOODWILL_CG_W4` | `0.25` | Weight for SS in CG equation |
| `GOODWILL_UGS_W1` | `0.5` | Weight for G in UGS equation |
| `GOODWILL_UGS_W2` | `0.5` | Weight for CG in UGS equation |

---

## License

This project is 100% open-source under the **MIT License**. You may use, modify, distribute, and sublicense it under the terms in the included `LICENSE` file.

## Enterprise Consulting & Integration
This architecture is fully open-source under the MIT License. If your organization requires custom scaling, proprietary integration, or dedicated technical consulting to deploy these models at an enterprise level, please reach out at: dfeen87@gmail.com

---
## Acknowledgments

The development of **Goodwill‑KPI** was strengthened by the contributions of several advanced AI systems. I extend my sincere thanks to **Microsoft Copilot**, **Anthropic Claude Sonnet**, and **Google Jules** for their substantial assistance throughout this project. Their combined reasoning, analysis, and generative support played a meaningful role in refining the architecture, documentation, and overall clarity of the framework.

This work reflects a collaborative spirit across tools and disciplines, and I’m grateful for the capabilities that helped bring Goodwill‑KPI to a professional, governance‑ready standard.
