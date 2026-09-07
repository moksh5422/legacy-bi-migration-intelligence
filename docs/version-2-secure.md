# Version 2 — Secure

The second version treats access as an application concern rather than an LLM concern.

## Flow

```text
User identity
    |
    v
RBAC / scope check
    |
    +---- DENY -> stop
    |
    v
PII / policy checks
    |
    v
AI or tool operation
```

The model never decides what a user is allowed to access. Sensitive fields can be detected or redacted before they reach an AI path, and tool calls can be rejected when the caller does not have the required scope.

This also makes audit and troubleshooting easier because authorization decisions are explicit and testable.
