# Legacy BI Migration Intelligence

A focused reference implementation for a difficult enterprise migration problem: **how can AI reduce the investigation and mapping work in a legacy BI migration without making the model responsible for security, correctness, or release decisions?**

The reference is based on a migration pattern involving **81 Spotfire reports**, multiple source systems, legacy transformations, calculated fields, filters, and business rules, with **Power BI and Microsoft Fabric** as the target platform.

The public repository is intentionally sanitized. It uses synthetic data and local interfaces; it does not contain client data, proprietary report definitions, credentials, or confidential implementation details.

## What is actually implemented here

The repository contains a runnable Python workflow that demonstrates the core pattern end to end:

```text
Synthetic legacy report
        |
        v
Discovery / inventory
        |
        v
Migration planning
        |
        v
AI-assisted migration analysis
        |
        +------------------+
        |                  |
        v                  v
 PII / security       Migration spec
        |                  |
        +--------+---------+
                 |
                 v
        Synthetic ETL
 Extract -> Transform -> Curate
                 |
                 v
              Lineage
                 |
                 v
        Deterministic checks
                 |
        +--------+--------+
        |                 |
       PASS             REVIEW
        |                 |
        +--------+--------+
                 v
       Evaluation + review queue
```

The LLM is optional. Without Azure credentials, the same flow runs using deterministic fallback logic so the project can be cloned and exercised locally.

## Three versions of the solution

### V1 — Understand the legacy workload

A report is turned into structured metadata containing sources, calculations, filters, transformations, and dependencies.

The migration agent can use Azure OpenAI to interpret unfamiliar expressions and propose where logic should live:

```text
legacy expression
      -> interpretation
      -> proposed target layer
      -> confidence
      -> review when ambiguous
```

The model proposes; it does not approve the migration.

### V2 — Secure the workflow

The application is the security boundary.

RBAC is checked before data or tools are accessed. PII-like fields can be detected before an AI path is used. The public demo uses synthetic inputs to illustrate the control points.

```text
identity
  -> authorization
  -> PII policy
  -> allowed operation
  -> AI / tool
```

### V3 — Evaluate and improve performance

Migration acceptance uses deterministic reconciliation rather than an LLM judgment.

The repository also includes an evaluation contract for RAGAS metrics and a lightweight telemetry utility for timing pipeline steps. The RAGAS file is a synthetic fixture; a real deployment would connect it to a secured RAG evaluation dataset.

The performance view is the full request path:

```text
request -> retrieval -> context -> model -> response
```

Caching and SSE are documented as the next production layer; the migration workload represented by this project saw approximately **250 ms P95 improvement** during performance work.

## Agents and controls

| Component | Role in the workflow | Implemented in demo |
|---|---|---|
| Discovery Agent | Builds report/source/calculation inventory | Yes |
| Planning Agent | Scores complexity and orders work | Yes |
| Migration Agent | Interprets legacy expressions and proposes mappings | Yes; Azure OpenAI optional |
| Security / RBAC | Enforces scope before operations | Yes |
| PII Control | Flags sensitive-looking fields | Yes |
| Similarity / reuse | Identifies repeated expressions | Present in agent module |
| Evaluation Agent | Applies confidence/review gates | Yes |
| MCP tool boundary | Represents an allow-listed tool surface | Yes, local registry |
| ETL | Extract, normalize, transform, curate | Yes |
| Lineage | Maps source logic to target layer | Yes |
| Reconciliation | Compares old/new values deterministically | Yes |
| Review Queue | Collects mapping, security, and validation exceptions | Yes |
| RAGAS | Evaluation contract / fixture | Fixture included |
| Observability | Step-level timing | Yes |
| CI/CD | Tests + runnable demo on push/PR | Yes |

## End-to-end example

The synthetic report describes revenue, customer segmentation, a region filter, two upstream sources, and a normalization rule.

The ETL layer reads synthetic CSV data, normalizes values, applies the business rule, and creates a curated output. The migration workflow then checks authorization, builds lineage, compares source and target metrics, and creates a review queue when something does not reconcile.

Run the full workflow from the repository root:

```bash
python -m venv .venv

# Windows
.venv\\Scripts\\activate

pip install -r requirements.txt
python -m demo.app
python pipeline/run.py
pytest -q
```

### Azure OpenAI mode

Copy `demo/.env.example` to `demo/.env` and provide the approved Azure OpenAI endpoint, deployment, key, and API version.

The model is used for interpretation only. Authorization, validation, reconciliation, and release decisions remain in code.

## Migration manifest and lineage

The intended production pattern is to normalize each report into a migration contract containing:

```text
report
sources
transformations
calculations
filters
dependencies
status
confidence
review items
```

Lineage then connects the source logic to its target layer:

```text
source field
   -> transformation
   -> curated data
   -> semantic-model measure
   -> Power BI report
```

This is useful when the same business rule appears in multiple reports because the rule can be identified before it is rebuilt repeatedly.

## Human review and idempotency

A production migration would persist report hashes, migration status, validation results, and review decisions.

That enables:

```text
unchanged report -> skip
changed report   -> re-analyze
failed report    -> resume from checkpoint
ambiguous case   -> human queue
```

The public demo shows the review queue pattern; durable state would normally live in a database or workflow/orchestration service.

## Where AI belongs

Use AI where the task requires interpretation:

- legacy-expression understanding
- target-layer recommendations
- business-rule explanation
- similarity hints

Use deterministic code where the system needs guarantees:

- access control
- PII policy
- ETL transformations
- reconciliation
- acceptance criteria
- audit records

> **Use the model for interpretation. Use code for guarantees.**

## Repository structure

```text
legacy-bi-migration-intelligence/
├── README.md
├── requirements.txt
├── .github/
│   └── workflows/
│       └── ci.yml
├── demo/
│   ├── agents.py
│   ├── app.py
│   ├── models.py
│   ├── requirements.txt
│   ├── .env.example
│   └── sample_report.json
├── examples/
│   ├── legacy_report.json
│   └── sales.csv
├── pipeline/
│   ├── etl.py
│   ├── evaluation.py
│   ├── lineage.py
│   ├── observability.py
│   ├── planner.py
│   ├── review.py
│   ├── run.py
│   └── security.py
├── src/
│   └── validate/
│       └── reconciliation.py
└── tests/
    └── test_pipeline.py
```

## Scope of the public repository

This is a **sanitized reference implementation**, not the original enterprise codebase. The purpose is to show the structure of a solution that can sit around a real migration program while keeping proprietary artifacts private.
