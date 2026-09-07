# Legacy BI Migration Intelligence

A focused engineering project for a difficult enterprise migration problem: using AI to understand legacy BI logic without making the model responsible for security, correctness, or production performance.

This is a **sanitized portfolio implementation** based on a migration pattern involving **81 Spotfire reports**, multiple source systems, legacy transformations, calculated fields, filters, and business rules, with the target platform being **Power BI and Microsoft Fabric**.

No client data, proprietary report definitions, credentials, or confidential implementation details are included.

## The problem

A large BI migration is easy to describe as:

```text
Open report -> understand it -> rebuild it -> validate it -> repeat
```

The difficult part is everything hidden inside that loop: undocumented dependencies, calculations, transformation logic, inconsistent business rules, sensitive data, and the need to prove that the new result still matches the old one.

The approach here turns those repeated decisions into a workflow that can be applied across many reports.

## Three versions of the solution

### V1 — Understand the legacy workload

The first version focused on discovery and interpretation.

A report is converted into structured metadata containing sources, calculations, filters, transformations, and dependencies. An LLM can then help with interpretation tasks such as explaining unfamiliar expressions, suggesting a target implementation, grouping similar logic, and flagging ambiguous mappings.

The model produces a proposal. It does not declare the migration correct.

```text
Legacy report
    |
    v
Inventory + parsing
    |
    v
Dependency / transformation analysis
    |
    v
LLM-assisted mapping
    |
    v
Migration specification
```

### V2 — Secure the workflow

Once the workflow can reason over enterprise information, access becomes a separate engineering concern.

The application remains the security boundary. Identity and role-based access control are checked before an AI or tool operation is allowed. PII handling and guardrails are also applied around the AI path.

```text
Identity
   |
   v
RBAC / authorization
   |
   v
Allowed scope
   |
   v
AI or tool operation
```

The model can request an action; it cannot grant itself permission to perform it.

### V3 — Evaluate and improve performance

The final version focuses on trust and usability.

For AI components, **RAGAS** can be used to measure retrieval and answer quality when prompts, chunking, search settings, or models change. For the migration itself, deterministic reconciliation checks compare row counts, aggregates, measures, filters, and other business values.

Latency is treated as a full request-path problem rather than only a model problem:

```text
request
  -> retrieval
  -> context construction
  -> model call
  -> response delivery
```

Caching and **SSE streaming** are used where appropriate. The workload described by the project saw an improvement of approximately **250 ms at P95**.

## Agent design

The system deliberately uses agents only where interpretation or planning benefits from an LLM. Other responsibilities remain deterministic.

### Discovery / Inventory Agent

Builds a searchable view of report sources, tables, calculations, filters, relationships, and transformations.

### Migration Planning Agent

Looks across the report inventory and produces migration order, dependency information, complexity/risk signals, and a first-pass plan so engineers can focus on the harder cases first.

### Migration Analysis Agent

Interprets legacy expressions and recommends whether logic belongs in the Fabric transformation layer, the semantic model, or requires human review.

### Security / Policy Layer

Checks identity, scope, RBAC, PII rules, and allowed operations before AI or tool access. This is intentionally not delegated to the LLM.

### Similarity / Reuse Agent

Finds reports or calculations that use substantially similar business logic so common transformations and semantic definitions can be reused instead of migrated independently.

### Evaluation Agent

Checks confidence, review flags, and evaluation results and decides whether a migration can move forward or needs human review.

### Tool / MCP Layer

Provides controlled functions such as:

```text
list_report_dependencies()
get_transformation()
get_sample_data()
validate_report()
create_migration_spec()
submit_for_review()
```

RBAC remains in front of those tools.

### Deterministic Reconciliation Engine

Compares source and target outputs. It is intentionally code-driven rather than model-driven.

## End-to-end flow

```text
                         +----------------------+
                         | Migration Planner     |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Discovery Agent      |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Migration Agent      |
                         +----------+-----------+
                                    |
                  +-----------------+-----------------+
                  |                                   |
          +-------v--------+                    +-----v------+
          | Security Layer |                    | MCP / Tools |
          | RBAC / PII     |                    | controlled  |
          +-------+--------+                    +-----+------+
                  |                                   |
                  +-----------------+-----------------+
                                    |
                         +----------v-----------+
                         | Human Review Queue   |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Fabric Transformation|
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Semantic Model       |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Power BI Report       |
                         +----------+-----------+
                                    |
                    +---------------+---------------+
                    |               |               |
             +------v-----+   +-----v-----+   +-----v-----+
             | Reconcile  |   | RAGAS      |   | Latency   |
             | source vs  |   | evaluation |   | / caching |
             | target     |   |            |   | / SSE     |
             +------+-----+   +-----+------+   +-----+-----+
                    |               |               |
                    +---------------+---------------+
                                    |
                         +----------v-----------+
                         | Release / Review     |
                         +-----------------------+
```

## Working demo

The `demo/` folder contains a small VS Code-runnable implementation using synthetic input data.

### Run without Azure credentials

The project includes a deterministic fallback so the workflow can be demonstrated locally without an Azure subscription.

```bash
cd demo
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
python -m demo.app
```

### Run with Azure OpenAI

Copy `.env.example` to `.env` and provide the approved Azure OpenAI endpoint, deployment name, API key, and API version.

The migration agent then uses Azure OpenAI for interpretation while authorization, validation, and acceptance decisions remain in application code.

## What the demo shows

A synthetic report contains:

- two upstream data sources
- a region filter
- a revenue calculation
- a customer-segmentation calculation
- a transformation rule

The demo then runs the workflow:

```text
1. Migration analysis
2. Security authorization
3. Evaluation
4. Deterministic reconciliation
5. Final decision
```

One intentionally mismatched value produces a `REVIEW` result so the demo shows why a migration should not be accepted simply because an LLM produced a confident answer.

## Repository structure

```text
legacy-bi-migration-intelligence/
├── README.md
├── docs/
│   ├── architecture.md
│   ├── agent-design.md
│   ├── version-1-understand.md
│   ├── version-2-secure.md
│   └── version-3-evaluate-perform.md
├── examples/
│   └── legacy_report.json
├── demo/
│   ├── __init__.py
│   ├── app.py
│   ├── agents.py
│   ├── models.py
│   ├── sample_report.json
│   ├── requirements.txt
│   └── .env.example
└── src/
    └── validate/
        └── reconciliation.py
```

## Design principles

1. **Use the LLM for interpretation, not authority.**
2. **Keep authorization outside the model.**
3. **Keep important validation deterministic.**
4. **Make uncertainty visible instead of hiding it.**
5. **Automate the predictable cases and route exceptions to engineers.**
6. **Measure quality, cost, and latency as the system changes.**

## Portfolio note

This repository is a public, sanitized engineering demonstration. It intentionally uses synthetic examples rather than client artifacts.
