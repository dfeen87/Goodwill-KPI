# Goodwill-KPI

A deterministic, auditable framework for quantifying organizational and consumer goodwill.

## Core Equations

| Equation | Formula | Notes |
|---|---|---|
| General Goodwill (G) | `((CR·w1)+(ES·w2)+(BT·w3)+(RG·w(t))−NCB) / T` | Time-normalized |
| Consumer Goodwill (CG) | `(CS·w1)+(BR·w2)+(CA·w3)+(SS·w4)−NCB_consumer` | Instantaneous |
| Unified Goodwill Score (UGS) | `((G·w1)+(CG·w2)) / T` | Time-normalized |

All inputs must be normalized to **[0, 100]** before being passed to the functions.

---

## Goodwill Dashboard (Render Deployment)

A minimal, read-only HTTP dashboard for executing and visualizing Goodwill calculations.

> ⚠ **Scores are comparative indicators, not financial valuations.**

### What the dashboard does

- Accepts normalized metric inputs for G, CG, and UGS.
- Accepts configurable weights and time factor (T).
- Executes all equations **server-side** using the existing pure functions — no logic is duplicated.
- Displays individual term contributions and final scores.
- Clearly labels time-normalized vs instantaneous metrics and penalty terms.

### What the dashboard does NOT do

- No forecasting, optimization, or action suggestions.
- No state is stored, mutated, or persisted.
- No client-side goodwill calculation.

### Routes

| Route | Method | Description |
|---|---|---|
| `/health` | GET | Liveness probe — returns `{"status": "ok"}` |
| `/dashboard` | GET | Read-only calculation interface (HTML) |
| `/api/goodwill/calculate` | POST | Accepts JSON inputs; returns G, CG, UGS and term breakdowns |

### Local Run

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server (development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/dashboard` in a browser.

### Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

### Render Deployment

The repository includes a `render.yaml` that configures a **Render.com** web service.

1. Connect the repository to your Render account.
2. Render will automatically detect `render.yaml` and create the service.
3. The service binds to the port provided by Render via `$PORT`.

**Manual deployment steps (if YAML auto-deploy is not available):**

- Environment: Python
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Environment Variables

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