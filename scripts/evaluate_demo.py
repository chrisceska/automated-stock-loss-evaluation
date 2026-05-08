import argparse
import json
import sys
from pathlib import Path
from urllib import error, request


REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIO_FILE = REPO_ROOT / "demo" / "scenarios" / "stock-loss-scenarios.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate the stock loss demo against the live API and optional Foundry result outputs."
    )
    parser.add_argument("--api-base-url", help="Base URL for the mock API or deployed Azure Function.")
    parser.add_argument(
        "--results-file",
        help="Optional JSON file containing Foundry run results keyed by scenarioId.",
    )
    parser.add_argument(
        "--exercise-actions",
        action="store_true",
        help="POST the first expected action for each scenario to validate execution wiring.",
    )
    parser.add_argument(
        "--output-json",
        help="Optional path to write the evaluation report as JSON.",
    )
    args = parser.parse_args()
    if not args.api_base_url and not args.results_file:
        parser.error("Provide at least --api-base-url or --results-file.")
    return args


def load_scenarios() -> list[dict]:
    payload = json.loads(SCENARIO_FILE.read_text(encoding="utf-8"))
    return payload["scenarios"]


def load_results(results_file: str | None) -> dict[str, dict]:
    if not results_file:
        return {}

    payload = json.loads(Path(results_file).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {item["scenarioId"]: item for item in payload}
    if isinstance(payload, dict) and "results" in payload:
        return {item["scenarioId"]: item for item in payload["results"]}
    return payload


def http_json(url: str, method: str = "GET", body: dict | None = None) -> dict:
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, method=method, data=data, headers=headers)
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def evaluate_api(api_base_url: str, scenario: dict, exercise_actions: bool) -> tuple[list[str], list[str]]:
    scenario_id = scenario["scenarioId"]
    expected = scenario["expectedOutcome"]
    passes = []
    failures = []

    scenario_list = http_json(f"{api_base_url}/signals/scenarios")
    if scenario_id in scenario_list.get("scenarioIds", []):
        passes.append("Scenario is discoverable from /signals/scenarios")
    else:
        failures.append("Scenario is missing from /signals/scenarios")

    signal = http_json(f"{api_base_url}/signals/scenarios/{scenario_id}")
    if signal.get("anomalyType") == expected["anomalyType"]:
        passes.append("Signal anomaly type matches expected outcome")
    else:
        failures.append(
            f"Signal anomaly type mismatch: expected {expected['anomalyType']}, got {signal.get('anomalyType')}"
        )

    evidence = http_json(f"{api_base_url}/evidence/scenarios/{scenario_id}")
    if evidence.get("keyRecords"):
        passes.append("Evidence endpoint returned key records")
    else:
        failures.append("Evidence endpoint returned no key records")

    policy = http_json(f"{api_base_url}/policy/actions/{scenario_id}")
    actual_actions = set(policy.get("permittedActions", []))
    expected_actions = set(expected["actions"])
    if expected_actions.issubset(actual_actions):
        passes.append("Policy actions include the expected action set")
    else:
        failures.append("Policy actions do not include the expected action set")

    forecast = http_json(f"{api_base_url}/forecast/scenarios/{scenario_id}/features")
    if forecast.get("scenarioId") == scenario_id:
        passes.append("Forecast features endpoint returned the scenario payload")
    else:
        failures.append("Forecast features endpoint returned the wrong scenario payload")

    if exercise_actions:
        action = expected["actions"][0]
        execution = http_json(
            f"{api_base_url}/automation/actions",
            method="POST",
            body={"scenarioId": scenario_id, "action": action, "requestedBy": "evaluation-runner"},
        )
        if execution.get("status") == "accepted":
            passes.append(f"Execution endpoint accepted {action}")
        else:
            failures.append(f"Execution endpoint did not accept {action}")

    return passes, failures


def normalize_confidence_band(result: dict) -> str | None:
    if "confidenceBand" in result:
        return str(result["confidenceBand"]).lower()
    if "confidence" not in result:
        return None

    confidence = float(result["confidence"])
    if confidence >= 85:
        return "high"
    if confidence >= 70:
        return "medium"
    return "low"


def evaluate_foundry_result(scenario: dict, result: dict | None) -> tuple[list[str], list[str]]:
    expected = scenario["expectedOutcome"]
    passes = []
    failures = []

    if result is None:
        failures.append("No Foundry result found for scenario")
        return passes, failures

    if result.get("anomalyType") == expected["anomalyType"]:
        passes.append("Foundry anomaly type matches expected outcome")
    else:
        failures.append("Foundry anomaly type does not match expected outcome")

    result_root_cause = str(result.get("primaryRootCause", "")).lower()
    expected_root_cause = expected["primaryRootCause"].lower()
    if expected_root_cause in result_root_cause or result_root_cause in expected_root_cause:
        passes.append("Foundry primary root cause aligns with expected outcome")
    else:
        failures.append("Foundry primary root cause does not align with expected outcome")

    result_band = normalize_confidence_band(result)
    if result_band == expected["confidenceBand"]:
        passes.append("Foundry confidence band matches expected outcome")
    else:
        failures.append("Foundry confidence band does not match expected outcome")

    if result.get("decisionPath") == expected["decisionPath"]:
        passes.append("Foundry decision path matches expected outcome")
    else:
        failures.append("Foundry decision path does not match expected outcome")

    result_actions = set(result.get("actions", result.get("actionsSelected", [])))
    expected_actions = set(expected["actions"])
    if expected_actions.issubset(result_actions):
        passes.append("Foundry actions include the expected action set")
    else:
        failures.append("Foundry actions do not include the expected action set")

    return passes, failures


def main() -> int:
    args = parse_args()
    scenarios = load_scenarios()
    foundry_results = load_results(args.results_file)
    report = {"scenarioReports": [], "summary": {"passes": 0, "failures": 0}}

    for scenario in scenarios:
        scenario_report = {"scenarioId": scenario["scenarioId"], "passes": [], "failures": []}

        try:
            if args.api_base_url:
                passes, failures = evaluate_api(args.api_base_url.rstrip("/"), scenario, args.exercise_actions)
                scenario_report["passes"].extend(passes)
                scenario_report["failures"].extend(failures)
        except error.HTTPError as exc:
            scenario_report["failures"].append(f"API request failed with status {exc.code}")
        except error.URLError as exc:
            scenario_report["failures"].append(f"API request failed: {exc.reason}")

        if args.results_file:
            passes, failures = evaluate_foundry_result(scenario, foundry_results.get(scenario["scenarioId"]))
            scenario_report["passes"].extend(passes)
            scenario_report["failures"].extend(failures)

        report["scenarioReports"].append(scenario_report)
        report["summary"]["passes"] += len(scenario_report["passes"])
        report["summary"]["failures"] += len(scenario_report["failures"])

    for item in report["scenarioReports"]:
        print(f"Scenario: {item['scenarioId']}")
        for passed in item["passes"]:
            print(f"  PASS: {passed}")
        for failed in item["failures"]:
            print(f"  FAIL: {failed}")

    print(
        f"\nSummary: {report['summary']['passes']} passes, {report['summary']['failures']} failures across {len(report['scenarioReports'])} scenarios"
    )

    if args.output_json:
        Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    return 0 if report["summary"]["failures"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())