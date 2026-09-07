# Architecture

The design separates reasoning from guarantees.

```text
                          +----------------------+
                          | Migration Planner    |
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
           | Security Layer |                    | Tool / MCP |
           | RBAC + PII     |                    | boundary   |
           +-------+--------+                    +-----+------+
                   |                                   |
                   +-----------------+-----------------+
                                     |
                          +----------v-----------+
                          | Human Review Queue   |
                          +----------+-----------+
                                     |
                          +----------v-----------+
                          | Fabric Transform     |
                          +----------+-----------+
                                     |
                          +----------v-----------+
                          | Semantic Model       |
                          +----------+-----------+
                                     |
                          +----------v-----------+
                          | Power BI             |
                          +----------+-----------+
                                     |
                +--------------------+-------------------+
                |                    |                   |
         Reconciliation          RAGAS             Latency tests
         source vs target       AI quality         caching / SSE
                |                    |                   |
                +--------------------+-------------------+
                                     |
                              Release decision
```

## Responsibility split

**Agents** handle interpretation, planning, classification, and other work where language-model reasoning adds value.

**Application services** enforce identity, RBAC, PII policy, tool permissions, and workflow state.

**Deterministic checks** decide whether source and target values reconcile and whether release criteria are satisfied.

This prevents the model from becoming the security or correctness boundary.
