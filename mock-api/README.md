# Mock API

This service exposes the synthetic stock loss scenarios through the same endpoints referenced by the OpenAPI contracts in `openapi/`.

## Purpose

Use this service when you want the Foundry agents to call a live endpoint without needing ERP, WMS, POS, or ticketing system access.

## Endpoints

- `GET /signals/scenarios`
- `GET /signals/scenarios/{scenarioId}`
- `GET /evidence/scenarios/{scenarioId}`
- `GET /policy/decision-thresholds`
- `GET /policy/actions/{scenarioId}`
- `POST /automation/actions`
- `GET /forecast/scenarios/{scenarioId}/features`

## Run Locally

```powershell
pip install -r mock-api/requirements.txt
uvicorn stockloss_demo_api.app:app --reload --port 8000
```

## Build Foundry Assets Against This API

```powershell
python scripts/build_foundry_assets.py --model-deployment <MODEL_DEPLOYMENT> --vector-store-id <VECTOR_STORE_ID> --api-base-url http://localhost:8000
```

The script writes bundled agent definitions to `foundry/dist/` with the OpenAPI specifications inlined and the base URL rewritten.

## Azure Functions

Deployment instructions for Azure Functions are in `mock-api/azure-functions.md`.