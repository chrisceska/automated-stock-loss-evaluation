import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
FOUNDRY_DIR = REPO_ROOT / "foundry"
OPENAPI_DIR = REPO_ROOT / "openapi"

OPENAPI_TOOL_MAP = {
    "inventory_signals_api": "inventory-signals-api.yaml",
    "inventory_evidence_api": "inventory-evidence-api.yaml",
    "policy_rules_api": "policy-rules-api.yaml",
    "workflow_automation_api": "workflow-automation-api.yaml",
    "forecast_features_api": "forecast-features-api.yaml",
}

AGENT_FILES = [
    "orchestrator.agent.json",
    "anomaly-detection.agent.json",
    "evidence-collector.agent.json",
    "root-cause.agent.json",
    "decisioning.agent.json",
    "execution.agent.json",
    "prevention.agent.json",
]

IMPORT_ORDER = [
    "anomaly-detection.agent.json",
    "evidence-collector.agent.json",
    "root-cause.agent.json",
    "decisioning.agent.json",
    "execution.agent.json",
    "prevention.agent.json",
    "orchestrator.agent.json",
]


def load_openapi_spec(file_name: str, api_base_url: str) -> str:
    spec_path = OPENAPI_DIR / file_name
    spec_text = spec_path.read_text(encoding="utf-8")
    return re.sub(r"(?m)^(\s*-\s+url:\s+).+$", rf"\1{api_base_url}", spec_text, count=1)


def build_agent(agent_name: str, model_deployment: str, vector_store_id: str, api_base_url: str) -> dict:
    agent_path = FOUNDRY_DIR / agent_name
    agent = json.loads(agent_path.read_text(encoding="utf-8"))

    if agent.get("model", {}).get("id") == "<YOUR_MODEL_DEPLOYMENT_NAME>":
        agent["model"]["id"] = model_deployment

    for tool in agent.get("tools", []):
        if tool.get("type") == "file_search":
            vector_store_ids = tool.setdefault("options", {}).setdefault("vector_store_ids", [])
            if vector_store_ids == ["<VECTOR_STORE_ID>"]:
                tool["options"]["vector_store_ids"] = [vector_store_id]

        if tool.get("type") == "openapi":
            tool_id = tool.get("id")
            spec_file = OPENAPI_TOOL_MAP.get(tool_id)
            if spec_file:
                tool.setdefault("options", {})["specification"] = load_openapi_spec(spec_file, api_base_url)

    return agent


def write_output(agent_name: str, agent_payload: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / agent_name
    output_path.write_text(json.dumps(agent_payload, indent=2) + "\n", encoding="utf-8")


def assert_no_placeholders(agent_payload: dict, agent_name: str) -> None:
    serialized = json.dumps(agent_payload)
    unresolved = re.findall(r"<[^>]+>", serialized)
    if unresolved:
        joined = ", ".join(sorted(set(unresolved)))
        raise ValueError(f"Unresolved placeholders remain in {agent_name}: {joined}")


def write_manifest(output_dir: Path, model_deployment: str, vector_store_id: str, api_base_url: str) -> None:
    manifest = {
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "modelDeployment": model_deployment,
        "vectorStoreId": vector_store_id,
        "apiBaseUrl": api_base_url,
        "importOrder": IMPORT_ORDER,
        "files": AGENT_FILES,
    }
    (output_dir / "import-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Foundry-ready agent assets by inlining OpenAPI specs and replacing placeholders."
    )
    parser.add_argument("--model-deployment", required=True, help="Azure OpenAI model deployment name.")
    parser.add_argument("--vector-store-id", required=True, help="Azure AI Search vector store ID.")
    parser.add_argument("--api-base-url", required=True, help="Reachable base URL for the mock or deployed API.")
    parser.add_argument(
        "--output-dir",
        default=str(FOUNDRY_DIR / "dist"),
        help="Directory to write bundled agent definitions to.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)

    for agent_name in AGENT_FILES:
        built_agent = build_agent(
            agent_name=agent_name,
            model_deployment=args.model_deployment,
            vector_store_id=args.vector_store_id,
            api_base_url=args.api_base_url,
        )
        assert_no_placeholders(built_agent, agent_name)
        write_output(agent_name, built_agent, output_dir)

    write_manifest(output_dir, args.model_deployment, args.vector_store_id, args.api_base_url)

    print(f"Built {len(AGENT_FILES)} agent definitions and import-manifest.json in {output_dir}")


if __name__ == "__main__":
    main()