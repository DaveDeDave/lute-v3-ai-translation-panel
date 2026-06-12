from __future__ import annotations

from scripts.prefetch_model import read_prefetch_config


def test_prefetch_config_reads_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("MT_MODEL", "example/model")
    monkeypatch.setenv("MODEL_CACHE_DIR", str(tmp_path))

    model_id, cache_dir = read_prefetch_config()

    assert model_id == "example/model"
    assert cache_dir == tmp_path


import pytest


def test_prefetch_config_requires_model_and_cache_dir(monkeypatch):
    monkeypatch.delenv("MT_MODEL", raising=False)
    monkeypatch.delenv("MODEL_CACHE_DIR", raising=False)

    with pytest.raises(RuntimeError, match="MT_MODEL, MODEL_CACHE_DIR"):
        read_prefetch_config()


def test_prefetch_config_requires_cache_dir(monkeypatch):
    monkeypatch.setenv("MT_MODEL", "example/model")
    monkeypatch.delenv("MODEL_CACHE_DIR", raising=False)

    with pytest.raises(RuntimeError, match="MODEL_CACHE_DIR"):
        read_prefetch_config()
