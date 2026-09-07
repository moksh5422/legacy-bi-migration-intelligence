# Legacy BI Migration Intelligence

I worked on a migration where a large set of legacy Spotfire reports had to move to Power BI and Microsoft Fabric. The hard part was not rebuilding the charts. It was figuring out what the old reports were actually doing, moving the right logic to the right layer, and having enough checks in place to trust the result.

The production work is private, so this repository is a small, sanitized version of the approach. It uses made-up report definitions and sample data. The aim is to show the shape of the solution, not to reproduce any client code.

The migration pattern behind the project covered **81 Spotfire reports** and multiple upstream data sources.

## The problem I was trying to solve

A typical report migration looks like this:

```text
open report -> understand it -> rebuild it -> check numbers -> move on
```

That works for a few reports. It gets painful when the same investigation has to be repeated over and over.

The approach here turns that work into a pipeline. A report is first described in a common format. The workflow then inspects it, works out a migration plan, uses AI for the parts that need interpretation, applies security checks, moves synthetic data through an ETL step, and finally compares the result with the expected output.

The important boundary is simple: **AI can suggest. It does not get to approve the migration.**

## What the reference implementation does

```text
legacy report
     |
     v
inventory + planning
     |
     v
AI-assisted mapping
     |
     +--------------------+
     |                    |
     v                    v
security / PII        migration spec
     |                    |
     +---------+----------+
               |
               v
        extract / transform
               |
               v
          curated data
               |
               v
             lineage
               |
               v
       deterministic checks
               |
        +------+------+
        |             |
       PASS         REVIEW
```

Everything after the AI suggestion is intentionally straightforward to inspect and test.

## Three versions of the solution

### V1 — Make the old logic understandable

The first version is about discovery.

The workflow collects report sources, calculations, filters, transformations, and dependencies into a common structure. The migration agent can look at a legacy expression and suggest whether it belongs in a Fabric transformation or in the Power BI semantic model.

For something uncertain, the output carries a confidence score and a review item instead of pretending the answer is certain.

### V2 — Make the AI safe to use around enterprise data

The next problem is access.

RBAC and data checks happen in the application before an AI or tool operation is allowed. A simple PII check is included in the demo to show where sensitive fields can be caught before they are sent down an AI path.

The model never decides what a user is allowed to see.

### V3 — Make the result something you can trust

The final version adds the checks that matter after the demo works.

The ETL path is tested separately from the AI path. Source and target numbers are reconciled with normal code. The review queue captures cases that need an engineer instead of hiding them.

For the AI side, the project includes the shape of a RAGAS evaluation fixture. In a real deployment, that would be wired to a secured evaluation dataset rather than hard-coded sample values.

The project also includes simple timing and cache/state hooks. The underlying workload included performance work that improved P95 response time by roughly **250 ms**.

## Agents, without the hype

There are several named components in the demo, but they do not all need to be LLMs.

| Component | What it actually does |
|---|---|
| Discovery | Builds a report inventory |
| Planning | Scores complexity and helps order migration work |
| Migration | Interprets legacy calculations and proposes target layers; Azure OpenAI is optional |
| Security | Checks role and requested scope |
| PII check | Flags fields that should not enter an AI path |
| Similarity | Finds repeated expressions that may be reusable |
| Evaluation | Applies confidence/review rules |
| Tool boundary | Represents the small set of operations an agent could request |
| ETL | Extracts, cleans, transforms, and curates sample data |
| Lineage | Shows where a piece of logic ends up |
| Reconciliation | Compares source and target values |
| Review queue | Collects things an engineer still needs to decide |

That separation is deliberate. I would rather have boring code enforce permissions and correctness than ask a language model to do it.

## ETL example

The sample data goes through a small but real processing step:

```text
sales.csv
   |
   v
read rows
   |
   v
normalize region names
   |
   v
normalize amounts
   |
   v
apply customer segment rule
   |
   v
curated result
```

This mirrors the bigger migration decision of moving repeatable data logic into the Fabric side instead of leaving it scattered across individual reports.

## Lineage

The demo records a simple source-to-target path, for example:

```text
SalesAmount
   -> Revenue calculation
   -> semantic model
   -> Power BI report
```

and:

```text
Region
   -> NormalizeRegion
   -> curated data
   -> report filter
```

For a larger migration, the same idea can be used to identify shared business rules before they are rebuilt in several places.

## Idempotency and state

A migration job should not start from scratch every time it is run.

The repository keeps a hash of the report definition so that the basic decision can be:

```text
same report   -> skip
changed       -> re-analyze
failed step   -> resume
needs review  -> wait for engineer
```

The public version stores this locally. A production implementation would normally keep the state in a durable store.

## Evaluation and release gates

The rule I am using throughout the project is:

```text
AI output
   |
   v
confidence / policy checks
   |
   +---- review ----+
   |                |
   v                v
validation       engineer
   |
   v
release decision
```

This keeps the model out of the final approval path.

## Running it locally

From the repository root:

```bash
python -m venv .venv

# Windows
.venv\\Scripts\\activate

pip install -r requirements.txt
pytest -q
python -m demo.app
python pipeline/run.py
```

Azure OpenAI is optional. To use it, copy `demo/.env.example` to `demo/.env` and provide the approved endpoint, deployment, key, and API version. Without those values the migration analysis falls back to local rules.

## CI

GitHub Actions runs the tests and both runnable workflows on every push and pull request. The workflow sets the repository root on `PYTHONPATH` so the `pipeline` package is imported the same way locally and in CI.

## Repository layout

```text
legacy-bi-migration-intelligence/
├── README.md
├── requirements.txt
├── .gitignore
├── .github/workflows/ci.yml
├── demo/
├── examples/
├── pipeline/
├── docs/
└── tests/
```

## One thing I would not put in production as-is

This repository is a reference implementation. The local RBAC map, local state file, sample PII detection, and RAGAS fixture are there to demonstrate the control points. A production deployment would replace them with the organization's identity provider, durable state store, approved data-classification controls, real evaluation data, managed secrets, and platform integrations.

That distinction matters because the goal of the project is to show **how I would structure the engineering problem**, not to pretend a small GitHub demo is the same thing as an enterprise deployment.
