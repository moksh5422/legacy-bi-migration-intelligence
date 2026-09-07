# Agent Design

The workflow uses agents only where reasoning is useful.

| Component | Purpose | LLM? | Why |
|---|---|---:|---|
| Discovery Agent | Inventory sources, calculations, filters, transformations | Optional | Mostly structured extraction; deterministic parsing is preferred where possible |
| Planning Agent | Rank migration work and identify dependencies | Yes, where interpretation is needed | Helps turn report inventory into an engineering plan |
| Migration Agent | Interpret legacy expressions and suggest target layers | Yes | This is the main reasoning task |
| Security Policy | Enforce identity, RBAC, scope, and PII policy | No | Security must not depend on model behavior |
| Similarity Agent | Find repeated calculations and reuse opportunities | Optional | Useful for grouping similar business logic |
| Evaluation Agent | Route uncertain results to review | Mostly no | Confidence and policy thresholds are explicit |
| MCP / Tool Layer | Expose controlled operations | No | Tools should enforce permissions before execution |
| Reconciliation Engine | Compare source and target values | No | Correctness should be deterministic |

## Example tool surface

```text
list_report_dependencies()
get_transformation()
get_sample_data()
validate_report()
create_migration_spec()
submit_for_review()
```

The agent can choose a tool. The tool gateway still checks the caller's identity and scope before execution.

## Human review

A migration recommendation enters the review queue when:

- confidence is below the configured floor
- a dependency is missing
- the rule touches a sensitive field
- deterministic reconciliation fails
- the proposed target layer is ambiguous

The goal is not to eliminate engineers from the workflow. The goal is to spend engineering time on the cases where interpretation or judgment is actually required.
