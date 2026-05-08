# AI Agent Prompts

This folder contains the individual system prompts that make up the autonomous inventory reconciliation workflow for stock loss prevention.

## Files

### `01-orchestrator-agent.md`
Master controller prompt for validating anomalies, coordinating specialist agents, aggregating findings, scoring confidence, and deciding the next action path.

### `02-anomaly-detection-agent.md`
Detection prompt for identifying inventory discrepancies from POS, inventory, shipment, and baseline data while minimizing false positives.

### `03-root-cause-analysis-agent.md`
Reasoning prompt for correlating evidence across systems and producing the most likely root causes with ranked confidence.

### `04-evidence-collection-agent.md`
Grounding prompt for retrieving, normalizing, and tracing evidence from operational data sources such as ERP, WMS, logs, and documents.

### `05-decisioning-agent.md`
Decision engine prompt for choosing whether to auto-remediate, partially automate, or escalate based on confidence and impact.

### `06-execution-agent.md`
Workflow automation prompt for carrying out approved actions in ticketing, notifications, and monitoring systems with auditable results.

### `07-preventative-intelligence-agent.md`
Predictive prompt for identifying recurring loss patterns, forecasting risk, and recommending preventative controls.

### `08-design-summary.md`
Reference summary of the overall multi-agent architecture, operating model, and business objective behind the prompt set.
