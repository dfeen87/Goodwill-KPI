"""Tests for environment-driven config parsing robustness."""

import importlib

import pytest

import goodwill.config as config


@pytest.fixture(autouse=True)
def _restore_config():
    """Reload config after each test to undo importlib.reload side-effects.

    Teardown runs after monkeypatch (LIFO order), so the env variable has
    already been restored to its original state before config is reloaded.
    """
    yield
    importlib.reload(config)


def test_float_env_invalid_string_raises_clear_error(monkeypatch):
    monkeypatch.setenv("GOODWILL_G_W1", "not-a-float")
    with pytest.raises(ValueError, match="GOODWILL_G_W1"):
        importlib.reload(config)


def test_float_env_non_finite_raises_clear_error(monkeypatch):
    monkeypatch.setenv("GOODWILL_G_W1", "inf")
    with pytest.raises(ValueError, match="GOODWILL_G_W1"):
        importlib.reload(config)


def test_float_env_valid_value_loads(monkeypatch):
    monkeypatch.setenv("GOODWILL_G_W1", "0.33")
    reloaded = importlib.reload(config)
    assert reloaded.G_W1 == pytest.approx(0.33)
