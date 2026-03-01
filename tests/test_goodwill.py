"""
Unit tests for the Goodwill Quantification Framework.

Coverage:
- Mathematical correctness of compute_G, compute_CG, and compute_UGS.
- Backlash terms (NCB, NCB_consumer) reduce goodwill scores.
- Time normalization (T) divides results correctly.
- Input validation raises ValueError for out-of-range values.
- T validation raises ValueError for T <= 0.
- Boundary values (0 and 100) are accepted without error.
- Full end-to-end pipeline: G -> CG -> UGS.
"""

import pytest

from goodwill import config
from goodwill.metrics import (
    METRIC_MAX,
    METRIC_MIN,
    compute_CG,
    compute_G,
    compute_UGS,
)


# ---------------------------------------------------------------------------
# compute_G — General Goodwill
# G = ((CR·w1) + (ES·w2) + (BT·w3) + (RG·w(t)) − NCB) / T
# ---------------------------------------------------------------------------


class TestComputeG:
    def test_known_values(self):
        # (50*0.25 + 60*0.25 + 70*0.25 + 80*0.25 - 10) / 1
        # = (12.5 + 15 + 17.5 + 20 - 10) / 1 = 55.0
        result = compute_G(
            CR=50, ES=60, BT=70, RG=80, NCB=10, T=1,
            w1=0.25, w2=0.25, w3=0.25, w_t=0.25,
        )
        assert result == pytest.approx(55.0)

    def test_all_zero_inputs_yield_zero(self):
        result = compute_G(
            CR=0, ES=0, BT=0, RG=0, NCB=0, T=1,
            w1=0.25, w2=0.25, w3=0.25, w_t=0.25,
        )
        assert result == pytest.approx(0.0)

    def test_time_normalization_halves_result_when_T_doubles(self):
        kwargs = dict(CR=80, ES=80, BT=80, RG=80, NCB=0,
                      w1=0.25, w2=0.25, w3=0.25, w_t=0.25)
        g_t1 = compute_G(**kwargs, T=1)
        g_t2 = compute_G(**kwargs, T=2)
        assert g_t2 == pytest.approx(g_t1 / 2)

    def test_backlash_reduces_goodwill(self):
        kwargs = dict(CR=80, ES=80, BT=80, RG=80, T=1,
                      w1=0.25, w2=0.25, w3=0.25, w_t=0.25)
        g_clean = compute_G(**kwargs, NCB=0)
        g_dirty = compute_G(**kwargs, NCB=20)
        assert g_dirty < g_clean

    def test_backlash_reduces_goodwill_by_exact_amount(self):
        # With T=1, NCB is subtracted directly: delta = 20 / 1 = 20
        kwargs = dict(CR=80, ES=80, BT=80, RG=80, T=1,
                      w1=0.25, w2=0.25, w3=0.25, w_t=0.25)
        g_clean = compute_G(**kwargs, NCB=0)
        g_dirty = compute_G(**kwargs, NCB=20)
        assert g_clean - g_dirty == pytest.approx(20.0)

    def test_large_backlash_produces_negative_result(self):
        result = compute_G(
            CR=10, ES=10, BT=10, RG=10, NCB=100, T=1,
            w1=0.25, w2=0.25, w3=0.25, w_t=0.25,
        )
        assert result < 0

    def test_custom_weights_applied_correctly(self):
        # w1=1, others=0 → G = (CR - NCB) / T
        result = compute_G(
            CR=80, ES=50, BT=50, RG=50, NCB=10, T=1,
            w1=1.0, w2=0.0, w3=0.0, w_t=0.0,
        )
        assert result == pytest.approx(80.0 - 10.0)

    def test_default_weights_from_config(self):
        result = compute_G(CR=80, ES=80, BT=80, RG=80, NCB=0, T=1)
        expected = (
            (80 * config.G_W1) + (80 * config.G_W2) +
            (80 * config.G_W3) + (80 * config.G_W_T)
        ) / 1
        assert result == pytest.approx(expected)

    # --- input validation ---

    def test_CR_above_range_raises(self):
        with pytest.raises(ValueError, match="CR"):
            compute_G(CR=101, ES=50, BT=50, RG=50, NCB=0, T=1,
                      w1=0.25, w2=0.25, w3=0.25, w_t=0.25)

    def test_CR_below_range_raises(self):
        with pytest.raises(ValueError, match="CR"):
            compute_G(CR=-1, ES=50, BT=50, RG=50, NCB=0, T=1,
                      w1=0.25, w2=0.25, w3=0.25, w_t=0.25)

    def test_ES_above_range_raises(self):
        with pytest.raises(ValueError, match="ES"):
            compute_G(CR=50, ES=101, BT=50, RG=50, NCB=0, T=1,
                      w1=0.25, w2=0.25, w3=0.25, w_t=0.25)

    def test_BT_above_range_raises(self):
        with pytest.raises(ValueError, match="BT"):
            compute_G(CR=50, ES=50, BT=101, RG=50, NCB=0, T=1,
                      w1=0.25, w2=0.25, w3=0.25, w_t=0.25)

    def test_RG_above_range_raises(self):
        with pytest.raises(ValueError, match="RG"):
            compute_G(CR=50, ES=50, BT=50, RG=101, NCB=0, T=1,
                      w1=0.25, w2=0.25, w3=0.25, w_t=0.25)

    def test_NCB_above_range_raises(self):
        with pytest.raises(ValueError, match="NCB"):
            compute_G(CR=50, ES=50, BT=50, RG=50, NCB=101, T=1,
                      w1=0.25, w2=0.25, w3=0.25, w_t=0.25)

    def test_T_zero_raises(self):
        with pytest.raises(ValueError, match="T"):
            compute_G(CR=50, ES=50, BT=50, RG=50, NCB=0, T=0,
                      w1=0.25, w2=0.25, w3=0.25, w_t=0.25)

    def test_T_negative_raises(self):
        with pytest.raises(ValueError, match="T"):
            compute_G(CR=50, ES=50, BT=50, RG=50, NCB=0, T=-1,
                      w1=0.25, w2=0.25, w3=0.25, w_t=0.25)

    def test_boundary_min_accepted(self):
        result = compute_G(
            CR=METRIC_MIN, ES=METRIC_MIN, BT=METRIC_MIN,
            RG=METRIC_MIN, NCB=METRIC_MIN, T=1,
            w1=0.25, w2=0.25, w3=0.25, w_t=0.25,
        )
        assert isinstance(result, float)

    def test_boundary_max_accepted(self):
        result = compute_G(
            CR=METRIC_MAX, ES=METRIC_MAX, BT=METRIC_MAX,
            RG=METRIC_MAX, NCB=METRIC_MAX, T=1,
            w1=0.25, w2=0.25, w3=0.25, w_t=0.25,
        )
        assert isinstance(result, float)


# ---------------------------------------------------------------------------
# compute_CG — Consumer Goodwill
# CG = (CS·w1) + (BR·w2) + (CA·w3) + (SS·w4) − NCB_consumer
# ---------------------------------------------------------------------------


class TestComputeCG:
    def test_known_values(self):
        # 50*0.25 + 60*0.25 + 70*0.25 + 80*0.25 - 10
        # = 12.5 + 15 + 17.5 + 20 - 10 = 55.0
        result = compute_CG(
            CS=50, BR=60, CA=70, SS=80, NCB_consumer=10,
            w1=0.25, w2=0.25, w3=0.25, w4=0.25,
        )
        assert result == pytest.approx(55.0)

    def test_no_time_normalization(self):
        # CG has no T parameter — result is invariant to when it is called
        kwargs = dict(CS=80, BR=80, CA=80, SS=80, NCB_consumer=0,
                      w1=0.25, w2=0.25, w3=0.25, w4=0.25)
        assert compute_CG(**kwargs) == compute_CG(**kwargs)

    def test_backlash_reduces_goodwill(self):
        kwargs = dict(CS=80, BR=80, CA=80, SS=80,
                      w1=0.25, w2=0.25, w3=0.25, w4=0.25)
        cg_clean = compute_CG(**kwargs, NCB_consumer=0)
        cg_dirty = compute_CG(**kwargs, NCB_consumer=20)
        assert cg_dirty < cg_clean

    def test_backlash_reduces_goodwill_by_exact_amount(self):
        kwargs = dict(CS=80, BR=80, CA=80, SS=80,
                      w1=0.25, w2=0.25, w3=0.25, w4=0.25)
        cg_clean = compute_CG(**kwargs, NCB_consumer=0)
        cg_dirty = compute_CG(**kwargs, NCB_consumer=20)
        assert cg_clean - cg_dirty == pytest.approx(20.0)

    def test_large_backlash_produces_negative_result(self):
        result = compute_CG(
            CS=10, BR=10, CA=10, SS=10, NCB_consumer=100,
            w1=0.25, w2=0.25, w3=0.25, w4=0.25,
        )
        assert result < 0

    def test_custom_weights_applied_correctly(self):
        # w1=1, others=0 → CG = CS - NCB_consumer
        result = compute_CG(
            CS=70, BR=50, CA=50, SS=50, NCB_consumer=10,
            w1=1.0, w2=0.0, w3=0.0, w4=0.0,
        )
        assert result == pytest.approx(70.0 - 10.0)

    def test_default_weights_from_config(self):
        result = compute_CG(CS=80, BR=80, CA=80, SS=80, NCB_consumer=0)
        expected = (
            (80 * config.CG_W1) + (80 * config.CG_W2) +
            (80 * config.CG_W3) + (80 * config.CG_W4)
        )
        assert result == pytest.approx(expected)

    # --- input validation ---

    def test_CS_above_range_raises(self):
        with pytest.raises(ValueError, match="CS"):
            compute_CG(CS=101, BR=50, CA=50, SS=50, NCB_consumer=0,
                       w1=0.25, w2=0.25, w3=0.25, w4=0.25)

    def test_BR_below_range_raises(self):
        with pytest.raises(ValueError, match="BR"):
            compute_CG(CS=50, BR=-1, CA=50, SS=50, NCB_consumer=0,
                       w1=0.25, w2=0.25, w3=0.25, w4=0.25)

    def test_CA_above_range_raises(self):
        with pytest.raises(ValueError, match="CA"):
            compute_CG(CS=50, BR=50, CA=101, SS=50, NCB_consumer=0,
                       w1=0.25, w2=0.25, w3=0.25, w4=0.25)

    def test_SS_above_range_raises(self):
        with pytest.raises(ValueError, match="SS"):
            compute_CG(CS=50, BR=50, CA=50, SS=101, NCB_consumer=0,
                       w1=0.25, w2=0.25, w3=0.25, w4=0.25)

    def test_NCB_consumer_above_range_raises(self):
        with pytest.raises(ValueError, match="NCB_consumer"):
            compute_CG(CS=50, BR=50, CA=50, SS=50, NCB_consumer=101,
                       w1=0.25, w2=0.25, w3=0.25, w4=0.25)

    def test_NCB_consumer_below_range_raises(self):
        with pytest.raises(ValueError, match="NCB_consumer"):
            compute_CG(CS=50, BR=50, CA=50, SS=50, NCB_consumer=-1,
                       w1=0.25, w2=0.25, w3=0.25, w4=0.25)

    def test_boundary_min_accepted(self):
        result = compute_CG(
            CS=METRIC_MIN, BR=METRIC_MIN, CA=METRIC_MIN,
            SS=METRIC_MIN, NCB_consumer=METRIC_MIN,
            w1=0.25, w2=0.25, w3=0.25, w4=0.25,
        )
        assert isinstance(result, float)

    def test_boundary_max_accepted(self):
        result = compute_CG(
            CS=METRIC_MAX, BR=METRIC_MAX, CA=METRIC_MAX,
            SS=METRIC_MAX, NCB_consumer=METRIC_MAX,
            w1=0.25, w2=0.25, w3=0.25, w4=0.25,
        )
        assert isinstance(result, float)


# ---------------------------------------------------------------------------
# compute_UGS — Unified Goodwill Score
# UGS = ((G·w1) + (CG·w2)) / T
# ---------------------------------------------------------------------------


class TestComputeUGS:
    def test_known_values(self):
        # ((60*0.5) + (40*0.5)) / 2 = 50 / 2 = 25.0
        result = compute_UGS(G=60, CG=40, T=2, w1=0.5, w2=0.5)
        assert result == pytest.approx(25.0)

    def test_time_normalization_halves_result_when_T_doubles(self):
        ugs_t1 = compute_UGS(G=60, CG=40, T=1, w1=0.5, w2=0.5)
        ugs_t2 = compute_UGS(G=60, CG=40, T=2, w1=0.5, w2=0.5)
        assert ugs_t2 == pytest.approx(ugs_t1 / 2)

    def test_equal_weights_with_T1(self):
        # UGS = (G*0.5 + CG*0.5) / 1
        result = compute_UGS(G=80, CG=60, T=1, w1=0.5, w2=0.5)
        assert result == pytest.approx((80 * 0.5 + 60 * 0.5) / 1)

    def test_negative_G_propagates(self):
        # Negative G (caused by high backlash) propagates through UGS
        result = compute_UGS(G=-10, CG=50, T=1, w1=0.5, w2=0.5)
        assert result == pytest.approx((-10 * 0.5 + 50 * 0.5) / 1)

    def test_default_weights_from_config(self):
        result = compute_UGS(G=80, CG=60, T=1)
        expected = ((80 * config.UGS_W1) + (60 * config.UGS_W2)) / 1
        assert result == pytest.approx(expected)

    def test_T_zero_raises(self):
        with pytest.raises(ValueError, match="T"):
            compute_UGS(G=60, CG=40, T=0, w1=0.5, w2=0.5)

    def test_T_negative_raises(self):
        with pytest.raises(ValueError, match="T"):
            compute_UGS(G=60, CG=40, T=-5, w1=0.5, w2=0.5)


# ---------------------------------------------------------------------------
# Full pipeline integration: compute_G → compute_CG → compute_UGS
# ---------------------------------------------------------------------------


class TestFullPipeline:
    def test_end_to_end_known_values(self):
        # Manual verification:
        # G = ((90*0.25)+(85*0.25)+(80*0.25)+(75*0.25) - 5) / 4
        #   = (22.5 + 21.25 + 20 + 18.75 - 5) / 4
        #   = 77.5 / 4 = 19.375
        #
        # CG = (88*0.25)+(82*0.25)+(78*0.25)+(72*0.25) - 8
        #    = 22 + 20.5 + 19.5 + 18 - 8 = 72.0
        #
        # UGS = ((19.375*0.5) + (72.0*0.5)) / 4
        #     = (9.6875 + 36.0) / 4 = 45.6875 / 4 = 11.421875
        G = compute_G(
            CR=90, ES=85, BT=80, RG=75, NCB=5, T=4,
            w1=0.25, w2=0.25, w3=0.25, w_t=0.25,
        )
        CG = compute_CG(
            CS=88, BR=82, CA=78, SS=72, NCB_consumer=8,
            w1=0.25, w2=0.25, w3=0.25, w4=0.25,
        )
        UGS = compute_UGS(G=G, CG=CG, T=4, w1=0.5, w2=0.5)

        assert G == pytest.approx(19.375)
        assert CG == pytest.approx(72.0)
        assert UGS == pytest.approx(11.421875)

    def test_high_backlash_degrades_pipeline(self):
        G_clean = compute_G(
            CR=80, ES=80, BT=80, RG=80, NCB=0, T=2,
            w1=0.25, w2=0.25, w3=0.25, w_t=0.25,
        )
        G_dirty = compute_G(
            CR=80, ES=80, BT=80, RG=80, NCB=50, T=2,
            w1=0.25, w2=0.25, w3=0.25, w_t=0.25,
        )
        CG = compute_CG(
            CS=80, BR=80, CA=80, SS=80, NCB_consumer=0,
            w1=0.25, w2=0.25, w3=0.25, w4=0.25,
        )
        ugs_clean = compute_UGS(G=G_clean, CG=CG, T=2, w1=0.5, w2=0.5)
        ugs_dirty = compute_UGS(G=G_dirty, CG=CG, T=2, w1=0.5, w2=0.5)
        assert ugs_dirty < ugs_clean


class TestNumericInputValidation:
    def test_compute_G_rejects_non_finite_and_bool(self):
        with pytest.raises(ValueError, match="CR"):
            compute_G(CR=float("nan"), ES=50, BT=50, RG=50, NCB=0, T=1)
        with pytest.raises(ValueError, match="ES"):
            compute_G(CR=50, ES=float("inf"), BT=50, RG=50, NCB=0, T=1)
        with pytest.raises(ValueError, match="RG"):
            compute_G(CR=50, ES=50, BT=50, RG=True, NCB=0, T=1)

    def test_compute_CG_rejects_non_finite_and_bool(self):
        with pytest.raises(ValueError, match="CS"):
            compute_CG(CS=float("nan"), BR=50, CA=50, SS=50, NCB_consumer=0)
        with pytest.raises(ValueError, match="BR"):
            compute_CG(CS=50, BR=float("-inf"), CA=50, SS=50, NCB_consumer=0)
        with pytest.raises(ValueError, match="NCB_consumer"):
            compute_CG(CS=50, BR=50, CA=50, SS=50, NCB_consumer=False)

    def test_compute_UGS_rejects_non_finite_T_and_bool(self):
        with pytest.raises(ValueError, match="T"):
            compute_UGS(G=10, CG=20, T=float("nan"))
        with pytest.raises(ValueError, match="T"):
            compute_UGS(G=10, CG=20, T=float("inf"))
        with pytest.raises(ValueError, match="T"):
            compute_UGS(G=10, CG=20, T=True)
