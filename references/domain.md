# Domain Meaning and Model Boundaries

## Clarify meaning when needed

If terms, business rules, state, or consistency affect implementation choices, load this reference.
For a simple script or CRUD change with clear accepted rules, keep the existing simple structure.
Domain-driven design (DDD) helps clarify business meaning and necessary model boundaries.
It does not require a new architecture or folder layout.

1. Find accepted terms, relevant examples, and business-rule owners.
2. Identify each context where a term has a specific meaning and governing rules.
3. Identify translations, identifiers, and responsibilities at boundaries between those contexts.
4. Resolve correctness-critical ambiguity through [specification review](spec-review.md) before dependent work.
5. Keep proposed terms and models separate from accepted agreements.

A business context is a scope with consistent meanings and rule ownership.
Frontend and backend describe technical components. Their directory split does not establish a business context map.
One component can serve several business contexts. Several components can serve one context.
When evaluating proposed domain models from AI, use accepted terms.
Similar names do not establish equivalent meaning.

Example: Billing's Account means a billable customer relationship. Identity's Account means a login principal.
Their accepted contract relates these meanings by customer ID.
Keep those meanings and that translation explicit. Do not merge them merely because both use the word Account.
Any changed relationship remains a proposal until accepted through the project's existing authority.

## Select only necessary model tactics

State important invariants: conditions that accepted behavior requires to remain true.
Identify the actor or component responsible for updates and the required consistency of those updates.
When existing project terms and structures express these needs, use them.

| Actual need | Optional tactic |
| --- | --- |
| Identity persists while attributes change | An entity can retain that identity. |
| A value has meaning through its attributes | A value object can group validation and value equality. |
| State changes have accepted preconditions and outcomes | Explicit transitions can protect the state rules. |
| Several updates must preserve one invariant together | An aggregate or existing transaction boundary can define the consistency responsibility. |

Only if a tactic solves a current identity, value, state, invariant, or consistency problem, select it.
Do not infer transactional consistency from common vocabulary alone.
When updates cross consistency boundaries, record any accepted delay, reconciliation, or failure behavior.
Do not mandate microservices, CQRS, event sourcing, events, repositories, or fixed folder layers.
When accepted rules need no additional model tactics, keep scripts and CRUD simple.

## Protect accepted boundaries when useful

If recurring coupling threatens an accepted boundary, consider checks available in the existing project.
Architecture tests or static analysis can check prohibited dependencies, imports, or data access.
Derive these checks from accepted boundaries. Do not invent a layer rule merely because a tool can check it.
Record the checked boundary and the limits of the method.
Passing structural checks do not establish correct business behavior or complete workflow acceptance.
Use [testing guidance](testing.md) for accepted invariants, compatible interfaces, and required effects.
