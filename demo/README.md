# Demo Assets

This folder turns the repository from a design package into a runnable demo slice for Azure AI Foundry.

## Included Assets

- `scenarios/stock-loss-scenarios.json`: Synthetic retail discrepancy scenarios used to exercise the agents.
- `evaluations/expected-outcomes.md`: Expected outputs for each scenario so the workflow can be validated.

## Recommended Demo Path

Run the scenarios in this order:

1. `store-201-pos-decrement-failure`
2. `store-118-receiving-gap`
3. `store-044-recurring-shrink-pattern`

The first scenario is the cleanest end-to-end path because it should produce a high-confidence root cause and a low-risk automated action plan.

## How To Use In Foundry

1. Import the agent definitions from `foundry/`.
2. Map each OpenAPI tool in the agent definitions to the matching spec in `openapi/`.
3. Load the scenario payloads into your mock API, Function App, or test harness.
4. Run one scenario at a time and compare the agent outputs to `evaluations/expected-outcomes.md`.

## Demo Goal

Validate that the multi-agent workflow can:

- detect a discrepancy,
- gather traceable evidence,
- rank a likely cause,
- choose an action within guardrails, and
- recommend a prevention step.