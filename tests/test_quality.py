import pytest
from unittest.mock import MagicMock
from app.services.quality_service import _run_check


def test_row_count_check_passes():
    result = _run_check("ROW_COUNT", None, 1000, "pipeline-abc")
    assert "actual_value" in result
    assert "passed" in result
    assert result["actual_value"] >= 0


def test_null_rate_check():
    result = _run_check("NULL_RATE", "id", 0.0, "pipeline-abc")
    assert result["passed"] == (result["actual_value"] <= 0.0)


def test_schema_check_always_passes():
    result = _run_check("SCHEMA", None, None, "any-pipeline")
    assert result["passed"] is True


def test_distribution_check():
    result = _run_check("DISTRIBUTION", "processed_value", 3.0, "pipeline-abc")
    assert "Z-score" in result["details"]
