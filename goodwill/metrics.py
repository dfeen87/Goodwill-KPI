"""Goodwill Quantification Framework — Core Metric Functions.

This module implements three deterministic, auditable equations:

- :func:`compute_G`   — General Goodwill (time-averaged organizational goodwill)
- :func:`compute_CG`  — Consumer Goodwill (instantaneous consumer sentiment)
- :func:`compute_UGS` — Unified Goodwill Score (aggregate of G and CG)

**All functions are pure: no side effects, no global state, no I/O.**

Input normalization
-------------------
All raw metric inputs (CR, ES, BT, RG, NCB, CS, BR, CA, SS, NCB_consumer)
**must** be normalized to the closed interval [0, 100] before being passed to
these functions.  A ``ValueError`` is raised immediately if any input falls
outside this range.

Time factor (T)
---------------
``T`` must be passed explicitly to every function that accepts it.  It is
never inferred from wall-clock time.  ``T`` must be a positive number (T > 0).
It supports rolling-window semantics: set T to the length of the observation
window in whatever consistent unit the caller uses (e.g. quarters, months).

Backlash terms (NCB, NCB_consumer)
-----------------------------------
NCB and NCB_consumer are **first-class destructive forces**.  They are
subtracted as specified by the equations and are **never clamped or softened**
unless the caller explicitly pre-processes them.  A high backlash value will
produce a lower — or negative — goodwill score; this is by design.

Weight configuration
--------------------
Default weights are loaded from :mod:`goodwill.config`, which supports
override via environment variables.  Weights can also be supplied directly
as keyword arguments to any function in this module.
"""

from __future__ import annotations

import math
from numbers import Real

from goodwill import config

# ---------------------------------------------------------------------------
# Documented valid range for all raw metric inputs.
# ---------------------------------------------------------------------------

#: Minimum accepted value for any raw metric input.
METRIC_MIN: float = 0.0

#: Maximum accepted value for any raw metric input.
METRIC_MAX: float = 100.0


# ---------------------------------------------------------------------------
# Internal validation helpers
# ---------------------------------------------------------------------------


def _validate_metric(value: float, name: str) -> None:
    """Raise ``ValueError`` if *value* is outside [METRIC_MIN, METRIC_MAX]."""
    _validate_real_number(value, name)
    if not (METRIC_MIN <= value <= METRIC_MAX):
        raise ValueError(
            f"Input '{name}' = {value!r} is outside the expected range "
            f"[{METRIC_MIN}, {METRIC_MAX}].  Normalize the value before "
            f"calling this function."
        )


def _validate_T(T: float) -> None:
    """Raise ``ValueError`` if *T* is not a positive number."""
    _validate_real_number(T, "T")
    if T <= 0:
        raise ValueError(
            f"Time normalization factor T = {T!r} must be a positive number "
            f"(T > 0).  T must be passed explicitly and must not be inferred "
            f"from wall-clock time."
        )


def _validate_real_number(value: float, name: str) -> None:
    """Raise ``ValueError`` if *value* is not a finite real number."""
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(
            f"Input '{name}' = {value!r} must be a finite real number."
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compute_G(
    CR: float,
    ES: float,
    BT: float,
    RG: float,
    NCB: float,
    T: float,
    *,
    w1: float = config.G_W1,
    w2: float = config.G_W2,
    w3: float = config.G_W3,
    w_t: float = config.G_W_T,
) -> float:
    """Compute General Goodwill (G).

    **Formula**::

        G = ((CR·w1) + (ES·w2) + (BT·w3) + (RG·w(t)) − NCB) / T

    This equation represents **time-averaged organizational goodwill**.

    Parameters
    ----------
    CR:
        Customer Retention.  Range [0, 100].
    ES:
        Employee Satisfaction.  Range [0, 100].
    BT:
        Brand Trust.  Range [0, 100].
    RG:
        Revenue Growth.  Range [0, 100].
    NCB:
        Net Customer Backlash.  Range [0, 100].  Applied as a first-class
        destructive force; **not clamped**.
    T:
        Time normalization factor (T > 0).  Must be passed explicitly.
        Supports rolling windows.
    w1:
        Static weight for CR.  Default: ``config.G_W1``.
    w2:
        Static weight for ES.  Default: ``config.G_W2``.
    w3:
        Static weight for BT.  Default: ``config.G_W3``.
    w_t:
        Time-dependent weight w(t) for RG.  Default: ``config.G_W_T``.

    Returns
    -------
    float
        Time-averaged organizational goodwill.  **May be negative** when NCB
        is large relative to the weighted metric sum.

    Raises
    ------
    ValueError
        If any metric input is outside [0, 100], or if T ≤ 0.
    """
    _validate_metric(CR, "CR")
    _validate_metric(ES, "ES")
    _validate_metric(BT, "BT")
    _validate_metric(RG, "RG")
    _validate_metric(NCB, "NCB")
    _validate_T(T)

    return ((CR * w1) + (ES * w2) + (BT * w3) + (RG * w_t) - NCB) / T


def compute_CG(
    CS: float,
    BR: float,
    CA: float,
    SS: float,
    NCB_consumer: float,
    *,
    w1: float = config.CG_W1,
    w2: float = config.CG_W2,
    w3: float = config.CG_W3,
    w4: float = config.CG_W4,
) -> float:
    """Compute Consumer Goodwill (CG).

    **Formula**::

        CG = (CS·w1) + (BR·w2) + (CA·w3) + (SS·w4) − NCB_consumer

    This equation is **intentionally not time-normalized**.  It represents an
    **instantaneous consumer sentiment state**.

    Parameters
    ----------
    CS:
        Customer Satisfaction.  Range [0, 100].
    BR:
        Brand Reputation.  Range [0, 100].
    CA:
        Customer Advocacy.  Range [0, 100].
    SS:
        Service Speed.  Range [0, 100].
    NCB_consumer:
        Negative Consumer Backlash.  Range [0, 100].  Applied as a first-class
        destructive force; **not clamped**.
    w1:
        Weight for CS.  Default: ``config.CG_W1``.
    w2:
        Weight for BR.  Default: ``config.CG_W2``.
    w3:
        Weight for CA.  Default: ``config.CG_W3``.
    w4:
        Weight for SS.  Default: ``config.CG_W4``.

    Returns
    -------
    float
        Instantaneous consumer goodwill.  **May be negative** when
        NCB_consumer is large relative to the weighted metric sum.

    Raises
    ------
    ValueError
        If any metric input is outside [0, 100].
    """
    _validate_metric(CS, "CS")
    _validate_metric(BR, "BR")
    _validate_metric(CA, "CA")
    _validate_metric(SS, "SS")
    _validate_metric(NCB_consumer, "NCB_consumer")

    return (CS * w1) + (BR * w2) + (CA * w3) + (SS * w4) - NCB_consumer


def compute_UGS(
    G: float,
    CG: float,
    T: float,
    *,
    w1: float = config.UGS_W1,
    w2: float = config.UGS_W2,
) -> float:
    """Compute the Unified Goodwill Score (UGS).

    **Formula**::

        UGS = ((G·w1) + (CG·w2)) / T

    G and CG **must be normalized to compatible scales** by the caller before
    being passed to this function.  T enforces longitudinal consistency.

    Parameters
    ----------
    G:
        General Goodwill score (output of :func:`compute_G`).  The caller is
        responsible for ensuring G is on a scale compatible with CG.
    CG:
        Consumer Goodwill score (output of :func:`compute_CG`).  The caller
        is responsible for ensuring CG is on a scale compatible with G.
    T:
        Time normalization factor (T > 0).  Must be passed explicitly.
    w1:
        Weight for G.  Default: ``config.UGS_W1``.
    w2:
        Weight for CG.  Default: ``config.UGS_W2``.

    Returns
    -------
    float
        Unified goodwill score.  Inherits sign and magnitude from G and CG.

    Raises
    ------
    ValueError
        If T ≤ 0.
    """
    _validate_T(T)

    return ((G * w1) + (CG * w2)) / T
