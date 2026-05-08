# Automated Stock Loss Evaluation

This repository defines a multi-agent workflow for autonomous inventory reconciliation and stock loss prevention in retail environments.

The solution is designed to detect discrepancies, gather grounded evidence, identify likely root causes, determine the right remediation path, execute approved actions, and continuously recommend preventative controls.

![Autonomous inventory reconciliation architecture](img/stocklossanalysissolution.png)

## Overview

The architecture follows a closed-loop operational pattern:

Detection -> Evidence -> Root Cause -> Decision -> Execution -> Prevention

An orchestrator coordinates specialized agents so each step remains focused, auditable, and confidence-driven.

## Repository Structure

- `prompts/`: Source prompt files for each agent plus a design summary.
- `foundry/`: Azure AI Foundry agent definition files for the multi-agent system.
- `demo/`: Synthetic scenarios and validation baselines for a Foundry demo.
- `openapi/`: Mock OpenAPI tool contracts for the agents' external dependencies.
- `mock-api/`: FastAPI service that serves the synthetic scenarios through live endpoints.
- `stockloss_demo_api/`: Shared API implementation used by local FastAPI and Azure Functions.
- `scripts/`: Utility scripts for preparing deployable Foundry assets.
- `img/`: Supporting diagrams and visual assets.
- `README.md`: Root project overview.

## Prompt Catalog

The `prompts/` folder contains the system prompt definitions for each role in the workflow:

- `01-orchestrator-agent.md`: Coordinates investigation, aggregates findings, and determines next steps.
- `02-anomaly-detection-agent.md`: Detects inventory mismatches from POS, shipment, and inventory records.
- `03-root-cause-analysis-agent.md`: Produces ranked root cause hypotheses with supporting evidence and confidence.
- `04-evidence-collection-agent.md`: Retrieves and normalizes enterprise records used to ground decisions.
- `05-decisioning-agent.md`: Applies confidence thresholds to choose automation, partial automation, or escalation.
- `06-execution-agent.md`: Carries out approved downstream actions such as tickets, notifications, and workflows.
- `07-preventative-intelligence-agent.md`: Identifies recurring patterns and recommends preventative action.
- `08-design-summary.md`: Captures the architecture pattern and overall system objective.

See `prompts/README.md` for the folder-level descriptions.

## Foundry Assets

The `foundry/` folder contains Azure AI Foundry agent definitions aligned to the same workflow:

- `orchestrator.agent.json`
- `anomaly-detection.agent.json`
- `evidence-collector.agent.json`
- `root-cause.agent.json`
- `decisioning.agent.json`
- `execution.agent.json`
- `prevention.agent.json`

These definitions are the deployable counterpart to the prompt files and are intended for use in an Azure AI Foundry project.

## Demo Starter Kit

The repository now includes a minimal demo slice so the multi-agent design can be exercised with synthetic retail data:

- `demo/scenarios/stock-loss-scenarios.json`: three discrepancy scenarios with grounded signals, evidence, and expected outcomes.
- `demo/evaluations/expected-outcomes.md`: validation targets for the agents.
- `openapi/*.yaml`: mock tool contracts for signals, evidence retrieval, policy rules, workflow automation, and prevention features.

The most direct first run is `store-201-pos-decrement-failure`, followed by the receiving gap and recurring shrink scenarios.

## Runtime Path

To run the demo end to end:

1. Start the mock API in `mock-api/`.
2. Bundle the Foundry agent definitions with `scripts/build_foundry_assets.py`.
3. Import the generated agent files from `foundry/dist/` into Azure AI Foundry.
4. Run each scenario and compare the outputs to `demo/evaluations/expected-outcomes.md`.

To score the live API or captured Foundry outputs, run `scripts/evaluate_demo.py`. See `demo/evaluations/README.md` for examples.

To host the demo API on Azure Functions, use `function_app.py`, `host.json`, and `requirements.txt`. Deployment steps are in `mock-api/azure-functions.md`.

## Operating Model

- Use enterprise signals only: POS, ERP, WMS, logs, receipts, and related operational data.
- Keep actions auditable and reversible.
- Avoid direct financial adjustments.
- Escalate to a human when confidence does not justify autonomy.

## Objective

Replace manual reconciliation with an auditable, confidence-based, AI-driven inventory intelligence workflow for retail stock loss evaluation.
