"""Goodwill Dashboard — FastAPI application.

Routes
------
GET  /health                    → 200 OK (liveness probe)
GET  /dashboard                 → Read-only calculation interface (HTML)
POST /api/goodwill/calculate    → Execute goodwill equations server-side;
                                  returns G, CG, UGS and term breakdowns

Constraints
-----------
- All goodwill equations are executed server-side via the pure functions in
  ``goodwill.metrics``.  This module does NOT duplicate any equation logic.
- No state is stored, mutated, or persisted.
- No forecasting, optimization, or action suggestions are performed.
"""

from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from goodwill.metrics import compute_CG, compute_G, compute_UGS
from goodwill import config as _cfg

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Goodwill KPI Dashboard",
    description="Read-only governance view for Goodwill metric calculations.",
    version="1.0.0",
)

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=_TEMPLATES_DIR)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class GoodwillInput(BaseModel):
    """Normalized metric inputs for all three goodwill equations."""

    # General Goodwill (G) inputs — range [0, 100]
    CR: float = Field(..., ge=0, le=100, description="Customer Retention [0–100]")
    ES: float = Field(..., ge=0, le=100, description="Employee Satisfaction [0–100]")
    BT: float = Field(..., ge=0, le=100, description="Brand Trust [0–100]")
    RG: float = Field(..., ge=0, le=100, description="Revenue Growth [0–100]")
    NCB: float = Field(..., ge=0, le=100, description="Net Customer Backlash [0–100]")

    # Consumer Goodwill (CG) inputs — range [0, 100]
    CS: float = Field(..., ge=0, le=100, description="Customer Satisfaction [0–100]")
    BR: float = Field(..., ge=0, le=100, description="Brand Reputation [0–100]")
    CA: float = Field(..., ge=0, le=100, description="Customer Advocacy [0–100]")
    SS: float = Field(..., ge=0, le=100, description="Service Speed [0–100]")
    NCB_consumer: float = Field(
        ..., ge=0, le=100, description="Negative Consumer Backlash [0–100]"
    )

    # Time normalization factor — must be > 0
    T: float = Field(..., gt=0, description="Time normalization factor (T > 0)")

    # Optional weight overrides (G)
    g_w1: Optional[float] = Field(None, description="Weight for CR (default: config)")
    g_w2: Optional[float] = Field(None, description="Weight for ES (default: config)")
    g_w3: Optional[float] = Field(None, description="Weight for BT (default: config)")
    g_w_t: Optional[float] = Field(None, description="Weight w(t) for RG (default: config)")

    # Optional weight overrides (CG)
    cg_w1: Optional[float] = Field(None, description="Weight for CS (default: config)")
    cg_w2: Optional[float] = Field(None, description="Weight for BR (default: config)")
    cg_w3: Optional[float] = Field(None, description="Weight for CA (default: config)")
    cg_w4: Optional[float] = Field(None, description="Weight for SS (default: config)")

    # Optional weight overrides (UGS)
    ugs_w1: Optional[float] = Field(None, description="Weight for G in UGS (default: config)")
    ugs_w2: Optional[float] = Field(None, description="Weight for CG in UGS (default: config)")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", status_code=200)
def health() -> dict:
    """Liveness probe — returns 200 OK."""
    return {"status": "ok"}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    """Render the read-only Goodwill calculation interface."""
    return templates.TemplateResponse(request, "dashboard.html")


@app.post("/api/goodwill/calculate")
def calculate(inputs: GoodwillInput) -> JSONResponse:
    """Execute all goodwill equations server-side and return full breakdowns.

    All calculations are delegated to the pure functions in ``goodwill.metrics``.
    No state is persisted.  Results are fully traceable to inputs.
    """
    # Resolve weights — use explicit override or fall back to config defaults
    g_w1 = inputs.g_w1 if inputs.g_w1 is not None else _cfg.G_W1
    g_w2 = inputs.g_w2 if inputs.g_w2 is not None else _cfg.G_W2
    g_w3 = inputs.g_w3 if inputs.g_w3 is not None else _cfg.G_W3
    g_w_t = inputs.g_w_t if inputs.g_w_t is not None else _cfg.G_W_T

    cg_w1 = inputs.cg_w1 if inputs.cg_w1 is not None else _cfg.CG_W1
    cg_w2 = inputs.cg_w2 if inputs.cg_w2 is not None else _cfg.CG_W2
    cg_w3 = inputs.cg_w3 if inputs.cg_w3 is not None else _cfg.CG_W3
    cg_w4 = inputs.cg_w4 if inputs.cg_w4 is not None else _cfg.CG_W4

    ugs_w1 = inputs.ugs_w1 if inputs.ugs_w1 is not None else _cfg.UGS_W1
    ugs_w2 = inputs.ugs_w2 if inputs.ugs_w2 is not None else _cfg.UGS_W2

    # Execute equations (server-side, via pure functions — no duplication)
    G = compute_G(
        CR=inputs.CR, ES=inputs.ES, BT=inputs.BT, RG=inputs.RG,
        NCB=inputs.NCB, T=inputs.T,
        w1=g_w1, w2=g_w2, w3=g_w3, w_t=g_w_t,
    )
    CG = compute_CG(
        CS=inputs.CS, BR=inputs.BR, CA=inputs.CA, SS=inputs.SS,
        NCB_consumer=inputs.NCB_consumer,
        w1=cg_w1, w2=cg_w2, w3=cg_w3, w4=cg_w4,
    )
    UGS = compute_UGS(G=G, CG=CG, T=inputs.T, w1=ugs_w1, w2=ugs_w2)

    return JSONResponse(
        content={
            # Final scores
            "G": G,
            "CG": CG,
            "UGS": UGS,
            # G term contributions (time-normalized)
            "G_terms": {
                "CR_term": inputs.CR * g_w1,
                "ES_term": inputs.ES * g_w2,
                "BT_term": inputs.BT * g_w3,
                "RG_term": inputs.RG * g_w_t,
                "NCB_penalty": inputs.NCB,          # penalty — reduces G
                "T": inputs.T,                       # time normalization divisor
                "time_normalized": True,
            },
            # CG term contributions (instantaneous)
            "CG_terms": {
                "CS_term": inputs.CS * cg_w1,
                "BR_term": inputs.BR * cg_w2,
                "CA_term": inputs.CA * cg_w3,
                "SS_term": inputs.SS * cg_w4,
                "NCB_consumer_penalty": inputs.NCB_consumer,  # penalty — reduces CG
                "time_normalized": False,
            },
            # UGS term contributions
            "UGS_terms": {
                "G_term": G * ugs_w1,
                "CG_term": CG * ugs_w2,
                "T": inputs.T,
                "time_normalized": True,
            },
            # Weights used (for full traceability)
            "weights_used": {
                "g_w1": g_w1, "g_w2": g_w2, "g_w3": g_w3, "g_w_t": g_w_t,
                "cg_w1": cg_w1, "cg_w2": cg_w2, "cg_w3": cg_w3, "cg_w4": cg_w4,
                "ugs_w1": ugs_w1, "ugs_w2": ugs_w2,
            },
        }
    )
