import json
from pathlib import Path

from app.routers import internal


def test_read_json_returns_data_for_valid_file(tmp_path):
    report = tmp_path / "report.json"
    report.write_text(json.dumps({"status": "ok"}), encoding="utf-8")

    assert internal._read_json(report) == {"status": "ok"}


def test_read_json_returns_none_for_missing_file(tmp_path):
    assert internal._read_json(tmp_path / "missing.json") is None


def test_scan_csv_dir_counts_files_and_lines(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("header\none\ntwo\n", encoding="utf-8")

    result = internal._scan_csv_dir(tmp_path, with_lines=True)

    assert result["exists"] is True
    assert result["files"] == 1
    assert result["details"][0]["name"] == "data.csv"
    assert result["details"][0]["lines"] == 2


def test_scan_csv_dir_handles_missing_directory(tmp_path):
    result = internal._scan_csv_dir(tmp_path / "missing")

    assert result == {
        "exists": False,
        "files": 0,
        "total_size_kb": 0,
        "details": [],
    }


def test_run_command_reports_success():
    result = internal._run_command(["python", "--version"], timeout=10)

    assert result["available"] is True
    assert result["success"] is True
    assert result["returncode"] == 0


def test_first_ok_returns_first_success(monkeypatch):
    calls = []

    def fake_http_json(url, timeout=2):
        calls.append(url)
        if "bad" in url:
            return {"error": "unavailable"}
        return {"status": "ok"}

    monkeypatch.setattr(internal, "_http_json", fake_http_json)

    result, base_url = internal._first_ok(["http://bad", "http://good"], "/health")

    assert result == {"status": "ok"}
    assert base_url == "http://good"
    assert calls == ["http://bad/health", "http://good/health"]
