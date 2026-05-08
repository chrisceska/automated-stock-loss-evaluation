# Autonomous Inventory Reconciliation – Azure AI Foundry Agents

This repository contains multi-agent Azure AI Foundry configurations for building a fully autonomous stock loss detection, root cause analysis, and remediation system.

The solution replaces manual reconciliation with an AI-driven closed-loop system that:

*   Detects discrepancies in near real-time
*   Identifies root causes using enterprise data
*   Executes remediation actions automatically
*   Prevents recurring issues through predictive intelligence

***

# Architecture Overview

This system follows a multi-agent orchestration pattern:

Detection → Evidence → Root Cause → Decision → Execution → Prevention

A central Orchestrator Agent coordinates specialized agents, each responsible for a specific step in the lifecycle.

***

# Agents Included

orchestrator.agent.json

*   Coordinates workflow and decision flow

anomaly-detection.agent.json

*   Identifies inventory discrepancies

evidence-collector.agent.json

*   Collects supporting data

root-cause.agent.json

*   Determines likely causes

decisioning.agent.json

*   Selects appropriate remediation

execution.agent.json

*   Executes workflows and actions

prevention.agent.json

*   Predicts and prevents future issues

***

# Key Concepts

Multi-Agent Design  
Each agent is single-purpose and specialized. This improves accuracy, enables modular deployment, and simplifies orchestration.

Autonomy with Guardrails  
The system uses confidence-based decisioning:

*   High confidence → automatic execution
*   Medium confidence → partial automation
*   Low confidence → human escalation

Grounded AI (RAG)  
Agents use Azure AI Search and enterprise data sources to ensure outputs are traceable, auditable, and grounded.

Closed-Loop Intelligence  
The system continuously detects, acts, learns, and improves over time.

***

# Prerequisites

Azure Resources

*   Azure AI Foundry Project
*   Azure OpenAI model deployment (for example gpt-4.1 or gpt-4o)
*   Azure AI Search (vector store)
*   Data platform (ADLS, Fabric, Synapse, or Databricks)

Identity and Security

*   Managed Identity enabled
*   RBAC configured for APIs and data sources

***

# Configuration Steps

Step 1 – Update Model Deployment

Update the model name in each file:

"model": {  
"id": "\<YOUR\_MODEL\_DEPLOYMENT\_NAME>"  
}

***

Step 2 – Configure Vector Store

Update the vector store reference:

"vector\_store\_ids": \["\<YOUR\_VECTOR\_STORE\_ID>"]

Used by Orchestrator, Evidence, and Root Cause agents.

***

Step 3 – Define OpenAPI Tools

Example configuration:

"type": "openapi",  
"id": "inventory\_api",  
"options": {  
"specification": "\<OPENAPI\_SCHEMA>",  
"auth": {  
"type": "managed\_identity"  
}  
}

Typical APIs:

*   Inventory system (ERP/WMS)
*   POS transactions
*   Incident management (ServiceNow)
*   Workflow automation

Sample tool contracts for a live demo are included in the repo under `openapi/`:

*   `inventory-signals-api.yaml`
*   `inventory-evidence-api.yaml`
*   `policy-rules-api.yaml`
*   `workflow-automation-api.yaml`
*   `forecast-features-api.yaml`

***

Step 4 – Deploy Agents

Option A – Foundry Portal

*   Navigate to ai.azure.com
*   Go to Agents
*   Create agent and paste configuration

Option B – VS Code Foundry Toolkit

*   Open project
*   Add agent definition
*   Deploy to environment

## Bundling Repo Assets For Foundry

The checked-in agent files remain source templates. To produce deployable versions with inlined OpenAPI definitions, run:

```powershell
python scripts/build_foundry_assets.py --model-deployment <MODEL_DEPLOYMENT> --vector-store-id <VECTOR_STORE_ID> --api-base-url <API_BASE_URL>
```

This writes Foundry-ready files to `foundry/dist/`.

The output directory also includes `import-manifest.json`, which records the generated environment values and the recommended import order.

For local testing, start the mock service in `mock-api/` and use `http://localhost:8000` as the API base URL.

For the full import workflow, use `foundry/import-runbook.md`.

***

# Example Flow

1.  Detection Agent identifies mismatch
2.  Orchestrator triggers investigation
3.  Evidence Agent retrieves data
4.  Root Cause Agent identifies issue
5.  Decision Agent selects action
6.  Execution Agent performs remediation
7.  Prevention Agent identifies similar risks

***

# Outputs

Operational Outputs

*   Incident tickets
*   Alerts (Teams or email)
*   Cycle count requests

Analytical Outputs

*   Root cause summaries
*   Confidence scores
*   Impact estimates

Strategic Outputs

*   Risk patterns across stores
*   Preventative recommendations

***

# Customization

Add Additional Agents

*   Fraud detection
*   Computer vision (shelf monitoring)
*   Pricing anomaly detection

Enhance Data Integration

*   IoT sensors
*   SAP or Dynamics
*   Real-time streaming pipelines

Adjust Decision Policies

*   Modify confidence thresholds
*   Add compliance rules
*   Introduce approval workflows

***

# Design Considerations

Reliability

*   Implement retry and circuit breaker patterns
*   Ensure workflows are idempotent

Security

*   Use managed identity
*   Apply least-privilege access

Observability

*   Log all agent activity
*   Track accuracy and outcomes

***

# Business Impact

*   Significant reduction in manual reconciliation effort
*   Faster detection and resolution of discrepancies
*   Improved shrink mitigation
*   Scalable operations across locations

***

# Summary

This solution enables a shift from manual, reactive reconciliation to autonomous, AI-driven operational intelligence.

***

# Next Steps

*   Deploy agents into an Azure AI Foundry project
*   Connect the tool definitions to the sample contracts in `openapi/`
*   Load the synthetic scenarios from `demo/scenarios/stock-loss-scenarios.json`
*   Run the scenarios and compare outputs with `demo/evaluations/expected-outcomes.md`

***

If you want, I can also generate a **matching repo structure (folders + sample OpenAPI specs + deployment scripts)** so you can drop this into a live demo environment.
