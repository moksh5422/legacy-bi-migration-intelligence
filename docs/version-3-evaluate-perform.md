# Version 3 — Evaluate and Perform

The third version focuses on trust and response time.

## AI evaluation

Use RAGAS for retrieval and answer evaluation when the AI workflow is used to interpret legacy documentation or migration context. Track metrics such as context recall, answer relevance, and faithfulness across prompt, model, chunking, and search changes.

## Migration validation

Use deterministic checks for the migrated workload:

- row counts
- aggregates
- business measures
- filter behaviour
- distinct counts
- null handling

A mismatch becomes a review item rather than an automatic acceptance.

## Performance

Measure the whole path:

```text
request -> retrieval -> context construction -> model -> response
```

Useful engineering controls include caching, reducing unnecessary context, model routing, and SSE streaming. The workload described by this project saw approximately 250 ms P95 improvement as part of the performance work.

## CI/CD direction

A mature version can run evaluation and reconciliation automatically on relevant changes:

```text
commit
  |
  v
unit tests
  |
  v
RAGAS evaluation
  |
  v
migration reconciliation
  |
  v
latency check
  |
  v
release / review
```
