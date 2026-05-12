import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from fastapi import APIRouter

router = APIRouter(prefix="/api/internal", tags=["internal"])

APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_DIR.parents[2] if len(APP_DIR.parents) > 2 else Path("/app")
QUALITY_REPORT = APP_DIR / "reports" / "quality_reports.json"
DIAGNOSTIC_REPORTS = [
    PROJECT_ROOT / "data" / "audit" / "diagnostic_report.json",
    Path("/app/data/audit/diagnostic_report.json"),
]

PROMETHEUS_URLS = [
    os.getenv("PROMETHEUS_URL", "http://prometheus:9090"),
    "http://localhost:9090",
]
GRAFANA_URLS = [
    os.getenv("GRAFANA_URL", "http://grafana:3000"),
    "http://localhost:3001",
]


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _read_json(path):
    try:
        if path.exists():
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}
    return None


def _http_json(url, timeout=2):
    try:
        with urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return {"error": str(exc), "url": url}


def _first_ok(urls, path):
    last_error = None
    for base_url in urls:
        result = _http_json(f"{base_url}{path}")
        if "error" not in result:
            return result, base_url
        last_error = result
    return last_error or {"error": "service unavailable"}, None


def _prometheus_query(query):
    encoded = query.replace(" ", "%20").replace("[", "%5B").replace("]", "%5D").replace("{", "%7B").replace("}", "%7D").replace('"', "%22").replace("|", "%7C").replace("=", "%3D").replace("~", "~").replace(",", "%2C").replace("*", "%2A")
    result, _ = _first_ok(PROMETHEUS_URLS, f"/api/v1/query?query={encoded}")
    try:
        values = result["data"]["result"]
        if not values:
            return 0
        return float(values[0]["value"][1])
    except Exception:
        return None


def _prometheus_vector(query):
    encoded = query.replace(" ", "%20").replace("[", "%5B").replace("]", "%5D").replace("{", "%7B").replace("}", "%7D").replace('"', "%22").replace("|", "%7C").replace("=", "%3D").replace("~", "~").replace(",", "%2C").replace("*", "%2A")
    result, _ = _first_ok(PROMETHEUS_URLS, f"/api/v1/query?query={encoded}")
    try:
        return [
            {
                "metric": item.get("metric", {}),
                "value": float(item["value"][1]),
            }
            for item in result["data"]["result"]
        ]
    except Exception:
        return []


def _run_command(command, cwd=None, timeout=20):
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "available": True,
            "success": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout[-6000:],
            "stderr": completed.stderr[-3000:],
            "ran_at": _now(),
        }
    except FileNotFoundError as exc:
        return {"available": False, "success": False, "error": str(exc), "ran_at": _now()}
    except subprocess.TimeoutExpired as exc:
        return {"available": True, "success": False, "error": f"Timeout apres {exc.timeout}s", "ran_at": _now()}
    except Exception as exc:
        return {"available": False, "success": False, "error": str(exc), "ran_at": _now()}


def _docker_status():
    command = ["docker", "compose", "ps", "--format", "json"]
    result = _run_command(command, cwd=str(PROJECT_ROOT), timeout=8)
    services = []
    if result.get("success"):
        for line in result.get("stdout", "").splitlines():
            try:
                services.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    result["services"] = services
    return result


def _line_count(path):
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as file:
            return max(sum(1 for _ in file) - 1, 0)
    except Exception:
        return None


def _scan_csv_dir(path, recursive=False, with_lines=False):
    if not path.exists():
        return {"exists": False, "files": 0, "total_size_kb": 0, "details": []}

    files = sorted(path.rglob("*.csv") if recursive else path.glob("*.csv"))
    details = []
    for file in files:
        details.append(
            {
                "name": file.name,
                "path": str(file),
                "size_kb": round(file.stat().st_size / 1024, 2),
                "lines": _line_count(file) if with_lines else None,
            }
        )

    return {
        "exists": True,
        "files": len(files),
        "total_size_kb": round(sum(item["size_kb"] for item in details), 2),
        "details": details,
    }


def _quick_diagnostic_report(reason=None):
    data_dir = PROJECT_ROOT / "data"
    report = {
        "date_diagnostic": _now(),
        "projet": "ObRail Europe - MSPR E6.1",
        "mode": "quick_fallback",
        "reason": reason,
        "raw": _scan_csv_dir(data_dir / "raw", recursive=True, with_lines=False),
        "processed": _scan_csv_dir(data_dir / "processed", recursive=True, with_lines=False),
        "warehouse": _scan_csv_dir(data_dir / "warehouse", recursive=False, with_lines=True),
        "statut": "A_VERIFIER" if reason else "OK",
    }
    report_path = data_dir / "audit" / "diagnostic_report.json"
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=2, ensure_ascii=False)
    except Exception as exc:
        report["write_error"] = str(exc)
    return report


def _reports_summary():
    quality = _read_json(QUALITY_REPORT) or {}
    diagnostic = None
    for path in DIAGNOSTIC_REPORTS:
        diagnostic = _read_json(path)
        if diagnostic:
            break
    return {"quality": quality, "diagnostic": diagnostic}


@router.get("/overview")
def get_internal_overview():
    health = {"status": "ok", "checked_at": _now()}
    prometheus_targets, prometheus_url = _first_ok(PROMETHEUS_URLS, "/api/v1/targets")
    grafana_search, grafana_url = _first_ok(GRAFANA_URLS, "/api/search")
    reports = _reports_summary()

    active_targets = prometheus_targets.get("data", {}).get("activeTargets", []) if isinstance(prometheus_targets, dict) else []
    fastapi_target = next((target for target in active_targets if target.get("labels", {}).get("job") == "fastapi"), None)

    metrics = {
        "api_up": _prometheus_query('up{job="fastapi"}'),
        "requests_per_minute": _prometheus_query("sum(rate(http_requests_total[1m])) * 60"),
        "errors_5xx_per_second": _prometheus_query('sum(rate(http_requests_total{status=~"5..|5xx"}[1m])) or vector(0)'),
        "latency_p95_seconds": _prometheus_query("histogram_quantile(0.95, sum(rate(http_request_duration_highr_seconds_bucket[1m])) by (le))"),
        "latency_avg_seconds": _prometheus_query("sum(rate(http_request_duration_seconds_sum[1m])) / sum(rate(http_request_duration_seconds_count[1m]))"),
        "endpoints": _prometheus_vector("topk(10, sum(rate(http_requests_total[1m])) by (handler)) * 60"),
    }

    return {
        "generated_at": _now(),
        "health": health,
        "metrics": metrics,
        "prometheus": {
            "url": prometheus_url,
            "available": prometheus_url is not None,
            "target": fastapi_target,
            "targets": active_targets,
        },
        "grafana": {
            "url": grafana_url,
            "available": grafana_url is not None,
            "dashboards": grafana_search if isinstance(grafana_search, list) else [],
            "dashboard_url": "http://localhost:3001/d/obrail-api-monitoring/obrail-api-monitoring",
        },
        "docker": _docker_status(),
        "reports": reports,
    }


@router.post("/diagnostic/run")
def run_diagnostic():
    candidates = [
        PROJECT_ROOT / "etl" / "audit" / "diagnostic.py",
        Path("/app/etl/audit/diagnostic.py"),
    ]
    script = next((path for path in candidates if path.exists()), None)
    if not script:
        return {
            "success": False,
            "available": False,
            "error": "Script diagnostic.py introuvable depuis l'API",
            "ran_at": _now(),
        }

    result = _run_command([sys.executable, str(script)], cwd=str(script.parents[2]), timeout=60)
    report = _reports_summary().get("diagnostic")
    if not report:
        report = _quick_diagnostic_report(result.get("error") or result.get("stderr"))
        result["fallback"] = "quick_diagnostic_report"
    result["report"] = report
    return result


@router.post("/tests/run")
def run_tests():
    test_dir = PROJECT_ROOT / "platform" / "server" / "test"
    if not test_dir.exists():
        test_dir = Path("/app/test")
    if not test_dir.exists():
        return {
            "success": False,
            "available": False,
            "error": "Dossier de tests introuvable depuis l'API",
            "ran_at": _now(),
        }
    return _run_command([sys.executable, "-m", "pytest", str(test_dir), "-q"], cwd=str(test_dir.parent), timeout=120)
