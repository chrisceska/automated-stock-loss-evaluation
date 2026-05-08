# Evaluation Runner

Use the evaluation runner to validate the live API and optionally score captured Foundry outputs against the expected scenario outcomes.

## API Validation

```powershell
python scripts/evaluate_demo.py --api-base-url http://127.0.0.1:8000 --exercise-actions
```

This checks that each scenario can be discovered, that the signal endpoint returns the expected anomaly type, that evidence records exist, that policy actions match the scenario definition, that the forecast endpoint responds, and that one approved action can be executed.

## Foundry Result Scoring

```powershell
python scripts/evaluate_demo.py --results-file demo/evaluations/sample-foundry-results.json
```

Accepted result file shapes:

- a JSON object keyed by `scenarioId`
- a JSON array of objects with `scenarioId`
- a JSON object containing a `results` array

Expected result fields:

- `scenarioId`
- `anomalyType`
- `primaryRootCause`
- `confidenceBand` or numeric `confidence`
- `decisionPath`
- `actions` or `actionsSelected`

## Combined Validation

```powershell
python scripts/evaluate_demo.py --api-base-url http://127.0.0.1:8000 --results-file demo/evaluations/sample-foundry-results.json --exercise-actions
```