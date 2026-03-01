"""Default weight configuration for the Goodwill Quantification Framework.

All weights are dimensionless scalars applied to normalized metric inputs.
They can be overridden at runtime via environment variables, enabling external
configuration without code changes.

Environment variable names follow the pattern::

    GOODWILL_<EQUATION>_<PARAM>

All defaults assume equal weighting within each equation. Adjust to reflect
organizational priorities, but document any deviation from defaults for
audit traceability.
"""

from __future__ import annotations

import math
import os


def _float_env(name: str, default: float) -> float:
    """Return a finite float from environment variable *name* or *default*."""
    val = os.environ.get(name)
    if val is None:
        return default

    try:
        parsed = float(val)
    except ValueError as exc:
        raise ValueError(
            f"Environment variable {name!r} must be parseable as float; got {val!r}."
        ) from exc

    if not math.isfinite(parsed):
        raise ValueError(
            f"Environment variable {name!r} must be a finite float; got {val!r}."
        )

    return parsed


# ---------------------------------------------------------------------------
# General Goodwill (G) weights
# G = ((CR·w1) + (ES·w2) + (BT·w3) + (RG·w(t)) − NCB) / T
# ---------------------------------------------------------------------------

# Weight for CR (Customer Retention)
G_W1: float = _float_env("GOODWILL_G_W1", 0.25)

# Weight for ES (Employee Satisfaction)
G_W2: float = _float_env("GOODWILL_G_W2", 0.25)

# Weight for BT (Brand Trust)
G_W3: float = _float_env("GOODWILL_G_W3", 0.25)

# Time-dependent weight w(t) for RG (Revenue Growth)
G_W_T: float = _float_env("GOODWILL_G_W_T", 0.25)


# ---------------------------------------------------------------------------
# Consumer Goodwill (CG) weights
# CG = (CS·w1) + (BR·w2) + (CA·w3) + (SS·w4) − NCB_consumer
# ---------------------------------------------------------------------------

# Weight for CS (Customer Satisfaction)
CG_W1: float = _float_env("GOODWILL_CG_W1", 0.25)

# Weight for BR (Brand Reputation)
CG_W2: float = _float_env("GOODWILL_CG_W2", 0.25)

# Weight for CA (Customer Advocacy)
CG_W3: float = _float_env("GOODWILL_CG_W3", 0.25)

# Weight for SS (Service Speed)
CG_W4: float = _float_env("GOODWILL_CG_W4", 0.25)


# ---------------------------------------------------------------------------
# Unified Goodwill Score (UGS) weights
# UGS = ((G·w1) + (CG·w2)) / T
# ---------------------------------------------------------------------------

# Weight for G (General Goodwill)
UGS_W1: float = _float_env("GOODWILL_UGS_W1", 0.5)

# Weight for CG (Consumer Goodwill)
UGS_W2: float = _float_env("GOODWILL_UGS_W2", 0.5)
