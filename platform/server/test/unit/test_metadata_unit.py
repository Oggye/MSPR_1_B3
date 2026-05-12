import json

import pytest
from fastapi import HTTPException

from app.routers import metadata


def test_quality_report_uses_file_when_available(tmp_path, monkeypatch):
    routers_dir = tmp_path / "platform" / "server" / "app" / "routers"
    reports_dir = tmp_path / "platform" / "server" / "app" / "reports"
    reports_dir.mkdir(parents=True)
    routers_dir.mkdir(parents=True)

    report = {"execution_date": "2026-01-01", "project": "test", "summary": {"success": True}}
    (reports_dir / "quality_reports.json").write_text(json.dumps(report), encoding="utf-8")

    monkeypatch.setattr(metadata.os.path, "abspath", lambda _: str(routers_dir / "metadata.py"))

    assert metadata.get_quality_report() == report


def test_quality_report_returns_default_when_file_is_missing(tmp_path, monkeypatch):
    routers_dir = tmp_path / "platform" / "server" / "app" / "routers"
    routers_dir.mkdir(parents=True)

    monkeypatch.setattr(metadata.os.path, "abspath", lambda _: str(routers_dir / "metadata.py"))

    result = metadata.get_quality_report()

    assert result["project"].startswith("ObRail")
    assert result["summary"]["success"] is True
    assert len(result["data_sources"]) >= 1


def test_quality_report_wraps_unexpected_errors(monkeypatch):
    monkeypatch.setattr(metadata.os.path, "dirname", lambda _: (_ for _ in ()).throw(RuntimeError("boom")))

    with pytest.raises(HTTPException) as exc:
        metadata.get_quality_report()

    assert exc.value.status_code == 500


def test_data_sources_catalog_has_expected_shape():
    result = metadata.get_data_sources()

    assert "sources" in result
    assert len(result["sources"]) >= 6
    assert {"id", "name", "url", "datasets"}.issubset(result["sources"][0])
