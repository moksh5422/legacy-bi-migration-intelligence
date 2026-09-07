# Version 1 — Understand

The first version addresses the discovery problem.

A report is converted into structured information before migration work starts. The AI layer helps interpret legacy expressions and suggest where the logic should live in the target platform.

## Flow

```text
Legacy report
   |
   v
Inventory
   |
   v
Dependencies + calculations
   |
   v
AI-assisted interpretation
   |
   v
Migration specification
```

The useful output is not a rewritten dashboard. It is a reviewable specification that an engineer can validate and use to implement the target model.
