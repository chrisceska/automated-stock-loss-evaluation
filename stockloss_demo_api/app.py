import json
import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIO_PATH = REPO_ROOT / "demo" / "scenarios" / "stock-loss-scenarios.json"


class ExecutionRequest(BaseModel):
    scenarioId: str
    action: str
    requestedBy: str | None = None


def resolve_scenario_path() -> Path:
    configured_path = os.getenv("STOCKLOSS_SCENARIO_PATH")
    if configured_path:
        return Path(configured_path)
    return DEFAULT_SCENARIO_PATH


@lru_cache(maxsize=1)
def load_scenarios() -> dict[str, dict]:
    payload = json.loads(resolve_scenario_path().read_text(encoding="utf-8"))
    return {scenario["scenarioId"]: scenario for scenario in payload["scenarios"]}


def get_scenario_or_404(scenario_id: str) -> dict:
    scenario = load_scenarios().get(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail=f"Unknown scenario: {scenario_id}")
    return scenario


def infer_data_sources(scenario: dict) -> list[str]:
    sources = ["ERP", "WMS", "POS"]
    evidence = scenario["evidence"]
    if "documentNotes" in evidence:
        sources.append("DocumentStore")
    if "priorIncidentIds" in evidence or "incidentNotes" in evidence:
        sources.append("IncidentManagement")
    return sources


def build_data_quality_notes(scenario: dict) -> list[str]:
    notes = ["Synthetic demo data; identifiers and timestamps are deterministic."]
    if scenario["scenarioId"] == "store-118-receiving-gap":
        notes.append("ERP posting timestamp is intentionally absent to simulate a sync gap.")
    if scenario["scenarioId"] == "store-044-recurring-shrink-pattern":
        notes.append("Prior incidents are summarized rather than expanded into raw records.")
    return notes


def infer_source_system(key: str) -> str:
    normalized_key = key.lower()
    if "pos" in normalized_key:
        return "POS"
    if "shipment" in normalized_key or "receipt" in normalized_key:
        return "WMS"
    if "erp" in normalized_key:
        return "ERP"
    if "incident" in normalized_key:
        return "IncidentManagement"
    return "DataLake"


def infer_staffing_risk(evidence: dict) -> str:
    note_blob = " ".join(evidence.get("incidentNotes", []))
    if "labor" in note_blob.lower() or "staff" in note_blob.lower():
        return "elevated"
    return "normal"


def target_system_for_action(action: str) -> str:
    if action == "create_incident_ticket":
        return "ServiceNow"
    if action == "notify_store_manager":
        return "Teams"
    if action == "trigger_cycle_count":
        return "WMS"
    if action == "flag_recurring_issue_pattern":
        return "RiskMonitoring"
    if action == "recommend_preventative_controls":
        return "OperationsReview"
    if action == "request_human_review":
        return "AnalystQueue"
    return "WorkflowEngine"


def create_app() -> FastAPI:
    api = FastAPI(
        title="Automated Stock Loss Demo API",
        version="1.0.0",
        description="Mock API that exposes synthetic stock loss scenarios for the Foundry demo.",
    )

    @api.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @api.get("/signals/scenarios")
    def list_signal_scenarios() -> dict:
        return {"scenarioIds": list(load_scenarios().keys())}

    @api.get("/signals/scenarios/{scenario_id}")
    def get_signal_scenario(scenario_id: str) -> dict:
        scenario = get_scenario_or_404(scenario_id)
        signals = scenario["signals"]
        return {
            "scenarioId": scenario["scenarioId"],
            "storeId": scenario["storeId"],
            "skuId": scenario["sku"]["skuId"],
            "anomalyType": scenario["expectedOutcome"]["anomalyType"],
            "varianceUnits": signals["varianceUnits"],
            "varianceAmount": signals["varianceAmount"],
            "timeWindow": scenario["timeWindow"],
        }

    @api.get("/evidence/scenarios/{scenario_id}")
    def get_scenario_evidence(scenario_id: str) -> dict:
        scenario = get_scenario_or_404(scenario_id)
        evidence = scenario["evidence"]
        key_records = []

        for key, value in evidence.items():
            if isinstance(value, str):
                key_records.append(
                    {
                        "recordId": value,
                        "sourceSystem": infer_source_system(key),
                        "timestamp": scenario["timeWindow"]["end"],
                    }
                )
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and item[:4] != "No ":
                        key_records.append(
                            {
                                "recordId": item,
                                "sourceSystem": infer_source_system(key),
                                "timestamp": scenario["timeWindow"]["end"],
                            }
                        )

        return {
            "scenarioId": scenario["scenarioId"],
            "dataSourcesQueried": infer_data_sources(scenario),
            "keyRecords": key_records,
            "summary": scenario["title"],
            "dataQualityNotes": build_data_quality_notes(scenario),
        }

    @api.get("/policy/decision-thresholds")
    def get_decision_thresholds() -> dict:
        return {
            "autoExecuteMinConfidence": 85,
            "partialAutomationMinConfidence": 70,
            "prohibitedActions": [
                "adjust_inventory_balance",
                "post_financial_writeoff",
            ],
        }

    @api.get("/policy/actions/{scenario_id}")
    def get_permitted_actions(scenario_id: str) -> dict:
        scenario = get_scenario_or_404(scenario_id)
        return {
            "scenarioId": scenario_id,
            "permittedActions": scenario["expectedOutcome"]["actions"],
        }

    @api.post("/automation/actions", status_code=202)
    def execute_approved_action(request: ExecutionRequest) -> dict:
        scenario = get_scenario_or_404(request.scenarioId)
        permitted_actions = set(scenario["expectedOutcome"]["actions"])
        if request.action not in permitted_actions:
            raise HTTPException(status_code=400, detail=f"Action not allowed for scenario: {request.action}")

        return {
            "action": request.action,
            "targetSystem": target_system_for_action(request.action),
            "status": "accepted",
            "auditId": f"AUD-{request.scenarioId}-{request.action}",
        }

    @api.get("/forecast/scenarios/{scenario_id}/features")
    def get_forecast_features(scenario_id: str) -> dict:
        scenario = get_scenario_or_404(scenario_id)
        signals = scenario["signals"]
        evidence = scenario["evidence"]

        return {
            "scenarioId": scenario_id,
            "historicalAnomalies": signals.get("historicalAnomalies", 1),
            "seasonalityPattern": evidence.get("shiftPattern", "none_detected"),
            "staffingRisk": infer_staffing_risk(evidence),
            "categoryRisk": scenario["sku"]["category"],
        }

    return api


app = create_app()
