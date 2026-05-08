# Azure Functions Deployment

This repo includes a Functions-compatible entry point at the repo root in `function_app.py` and runtime metadata in `host.json`.

## Deployment Shape

- Local development API: `stockloss_demo_api.app`
- Azure Functions entry point: `function_app.py`
- Functions dependencies: `requirements.txt`
- Scenario source: `demo/scenarios/stock-loss-scenarios.json`

## Prerequisites

- Azure subscription
- Azure Functions Core Tools v4
- Azure CLI
- A Python 3.11 or 3.12 compatible Functions environment

## Create Azure Resources

```powershell
az group create --name <RESOURCE_GROUP> --location <LOCATION>
az storage account create --name <STORAGE_ACCOUNT> --location <LOCATION> --resource-group <RESOURCE_GROUP> --sku Standard_LRS
az functionapp plan create --name <PLAN_NAME> --resource-group <RESOURCE_GROUP> --location <LOCATION> --sku Y1 --is-linux
az functionapp create --name <FUNCTION_APP_NAME> --resource-group <RESOURCE_GROUP> --storage-account <STORAGE_ACCOUNT> --plan <PLAN_NAME> --runtime python --runtime-version 3.11 --functions-version 4
```

## Configure App Settings

If you deploy the whole repo, the default scenario path works as-is. If you relocate the scenario file, set:

```powershell
az functionapp config appsettings set --name <FUNCTION_APP_NAME> --resource-group <RESOURCE_GROUP> --settings STOCKLOSS_SCENARIO_PATH="demo/scenarios/stock-loss-scenarios.json"
```

## Deploy

From the repository root:

```powershell
func azure functionapp publish <FUNCTION_APP_NAME> --python
```

## Verify

After deployment, validate the API:

```powershell
python scripts/evaluate_demo.py --api-base-url https://<FUNCTION_APP_NAME>.azurewebsites.net/api --exercise-actions
```

If you keep the default Functions auth level, include a function key when testing protected endpoints.

## Foundry Wiring

Rebuild the Foundry assets against the deployed base URL:

```powershell
python scripts/build_foundry_assets.py --model-deployment <MODEL_DEPLOYMENT> --vector-store-id <VECTOR_STORE_ID> --api-base-url https://<FUNCTION_APP_NAME>.azurewebsites.net/api
```