"""Goodwill Quantification Framework — public API."""

from goodwill.metrics import compute_CG, compute_G, compute_UGS

__version__ = "1.1.0"

__all__ = ["compute_G", "compute_CG", "compute_UGS", "__version__"]
