# Foundry Import Runbook

Use this runbook when moving from source templates to an importable Azure AI Foundry demo.

## 1. Prepare Inputs

- Azure OpenAI model deployment name
- Azure AI Search vector store ID
- Base URL for the mock API or Azure Function

## 2. Build Import Assets

```powershell
python scripts/build_foundry_assets.py --model-deployment <MODEL_DEPLOYMENT> --vector-store-id <VECTOR_STORE_ID> --api-base-url <API_BASE_URL>
```

Artifacts written to `foundry/dist/`:

- 7 agent JSON files
- `import-manifest.json`

## 3. Review The Manifest

Confirm that `foundry/dist/import-manifest.json` matches the intended environment:

- `modelDeployment`
- `vectorStoreId`
- `apiBaseUrl`
- `importOrder`

## 4. Import Into Azure AI Foundry

Import the generated agent JSON files from `foundry/dist/` in the order listed in `import-manifest.json`.

Recommended order:

1. anomaly-detection.agent.json
2. evidence-collector.agent.json
3. root-cause.agent.json
4. decisioning.agent.json
5. execution.agent.json
6. prevention.agent.json
7. orchestrator.agent.json

Import the orchestrator last so all specialized agents and tool-backed dependencies already exist.

## 5. Smoke-Test The Demo

Run the `store-201-pos-decrement-failure` scenario first, then proceed to the remaining scenarios.

Compare outputs against `demo/evaluations/expected-outcomes.md` or run:

```powershell
python scripts/evaluate_demo.py --results-file <FOUNDRY_RESULTS_JSON>
```

## 6. Troubleshooting

- If import fails, inspect the generated file rather than the source template in `foundry/`.
- If a tool call fails, confirm the OpenAPI server URL inside the generated JSON points at the intended API host.
- If retrieval fails, confirm the bundled agents reference the correct vector store ID.