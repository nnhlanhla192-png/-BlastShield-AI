import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()
from agent.diff_reader import DiffReader
from agent.risk_analyzer import RiskAnalyzer
from testers.check_executor import run_all

TARGET_APP_URL = os.environ.get("TARGET_APP_URL", "http://localhost:5000")


def build_verdict(results):
    failed = [r for r in results if not r["passed"]]
    if not failed:
        return "All checks passed.\nOverall verdict: PASS"
    lines = [f"FAILED ({r['pillar']}): {r['description']} - expected {r['expected_status']}, got {r['actual_status']}."
              for r in failed]
    lines.append("Overall verdict: FAIL.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--diff", required=True)
    args = parser.parse_args()
    diff_text = open(args.diff).read()

    print(f"[1/4] RECEIVE: {args.diff}")
    diff_data = DiffReader().parse_diff(diff_text)

    print("[2/4] DECIDE")
    plan = RiskAnalyzer().decide(diff_text, diff_data)
    print(f"      {plan['summary']} (risk: {plan['risk_level']}, keyword score: {plan['keyword_scan']['risk_score']})")

    print(f"[3/4] DO: {len(plan['checks'])} check(s) vs {TARGET_APP_URL}")
    results = run_all(plan["checks"], TARGET_APP_URL)
    for r in results:
        print(f"      [{'PASS' if r['passed'] else 'FAIL'}] {r['description']}")

    verdict = build_verdict(results)
    print("[4/4] RETURN\n" + "=" * 50 + f"\n{verdict}\n" + "=" * 50)
    os.makedirs("reports", exist_ok=True)
    json.dump({"plan": plan, "results": results, "verdict": verdict}, open("reports/last_run.json", "w"), indent=2)


if __name__ == "__main__":
    main()