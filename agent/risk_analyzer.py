import json
import os
from typing import Any, Dict
from anthropic import Anthropic


class RiskAnalyzer:
    SECURITY_KEYWORDS = ["auth", "login", "password", "token", "role", "admin", "session", "permission"]
    PERFORMANCE_KEYWORDS = ["for ", "while ", "query", "sleep", "cache", "loop", "db."]

    def keyword_scan(self, diff_data: Dict[str, Any]) -> Dict[str, Any]:
        added = diff_data.get("added_lines", [])
        removed = diff_data.get("removed_lines", [])
        content = " ".join(added + removed).lower()

        score = 10
        flags = []
        sec_hits = [k for k in self.SECURITY_KEYWORDS if k in content]
        if sec_hits:
            score += 40
            flags.append("security")
        perf_hits = [k for k in self.PERFORMANCE_KEYWORDS if k in content]
        if perf_hits:
            score += 25
            flags.append("performance")
        if added or removed:
            flags.append("functional")

        score = min(100, score)
        level = "CRITICAL" if score >= 75 else "HIGH" if score >= 50 else "MEDIUM" if score >= 25 else "LOW"
        return {"risk_score": score, "risk_level": level, "flagged_pillars": sorted(set(flags)),
                "security_keywords_found": sec_hits, "performance_keywords_found": perf_hits}

    def decide(self, diff_text: str, diff_data: Dict[str, Any]) -> Dict[str, Any]:
        scan = self.keyword_scan(diff_data)
        if os.environ.get("MOCK_LLM", "false").lower() == "true":
            return self._mock_decide(scan)

        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        system = """You are a senior QA engineer reviewing a diff for a small Flask app.
Respond with ONLY JSON:
{"summary": "...", "risk_level": "low|medium|high|critical",
 "pillars_at_risk": ["functional","performance","security"],
 "checks": [{"pillar": "...", "description": "...", "http_method": "GET|POST|PUT|DELETE",
             "path": "/users/2", "headers": {}, "body": null, "expect_status": 403}]}
Only checks expressible as one HTTP call against http://localhost:5000."""
        msg = f"Keyword scan (a hint): {json.dumps(scan)}\n\nDiff:\n{diff_text}"
        resp = client.messages.create(model="claude-sonnet-4-6", max_tokens=1500,
                                       system=system, messages=[{"role": "user", "content": msg}])
        raw = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        plan = json.loads(cleaned)
        plan["keyword_scan"] = scan
        return plan

    @staticmethod
    def _mock_decide(scan):
        if "security" in scan["flagged_pillars"]:
            return {"summary": "Keyword scan flagged an admin/role check change.",
                     "risk_level": scan["risk_level"].lower(), "pillars_at_risk": ["security", "functional"],
                     "checks": [{"pillar": "security", "description": "Non-admin must NOT delete a user",
                                 "http_method": "DELETE", "path": "/users/2", "headers": {}, "body": None,
                                 "expect_status": 403}],
                     "keyword_scan": scan}
        return {"summary": "No strong signal; basic check.", "risk_level": scan["risk_level"].lower(),
                 "pillars_at_risk": ["functional"],
                 "checks": [{"pillar": "functional", "description": "Home route should respond",
                             "http_method": "GET", "path": "/", "headers": {}, "body": None, "expect_status": 200}],
                 "keyword_scan": scan}