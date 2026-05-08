# Automated Stock Loss Evaluation

This repository contains the prompt set for an autonomous inventory reconciliation and stock loss prevention workflow.

The design models a multi-agent system that detects discrepancies, collects evidence, identifies likely root causes, decides the proper remediation path, executes approved actions, and recommends preventative controls.

![alt text](img/stocklossanalysissolution.png)


## Repository Structure

- `prompts/`: Individual agent prompts and design reference material.
- `readme.md`: Top-level overview of the project.

## Prompt Set

The prompt catalog is organized by agent responsibility:

- `01-orchestrator-agent.md`: Coordinates the end-to-end workflow and determines next actions.
- `02-anomaly-detection-agent.md`: Detects inventory discrepancies from operational data.
- `03-root-cause-analysis-agent.md`: Produces ranked root cause hypotheses with confidence.
- `04-evidence-collection-agent.md`: Retrieves and normalizes supporting records from source systems.
- `05-decisioning-agent.md`: Chooses automation, partial automation, or escalation.
- `06-execution-agent.md`: Executes approved workflow actions in downstream systems.
- `07-preventative-intelligence-agent.md`: Identifies recurring patterns and preventative actions.
- `08-design-summary.md`: Summarizes the architecture pattern and objective.

See `prompts/README.md` for the folder-level prompt descriptions.

## Objective

Replace manual reconciliation with an auditable, confidence-based, AI-driven inventory intelligence workflow for retail stock loss evaluation.
