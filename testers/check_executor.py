import requests


def run_check(check: dict, base_url: str) -> dict:
    url = base_url.rstrip("/") + check["path"]
    method = check.get("http_method", "GET")
    try:
        response = requests.request(method, url, headers=check.get("headers") or {},
                                     json=check.get("body"), timeout=10)
        return {"pillar": check["pillar"], "description": check["description"],
                "expected_status": check["expect_status"], "actual_status": response.status_code,
                "passed": response.status_code == check["expect_status"]}
    except requests.RequestException as e:
        return {"pillar": check["pillar"], "description": check["description"],
                "expected_status": check["expect_status"], "actual_status": None,
                "passed": False, "error": str(e)}


def run_all(checks: list, base_url: str) -> list:
    return [run_check(c, base_url) for c in checks]