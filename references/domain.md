# Business Terms and Model Boundaries

## Examine business terms when necessary

If terms, business rules, state, or consistency have effects on implementation decisions, read this reference.
For a script or CRUD change with clear accepted rules, keep the structure that the project uses.
Domain-driven design (DDD) helps make business terms and necessary model boundaries clear.
A new architecture or folder layout is not necessary.

For the domain behavior in this task, do these steps:

1. Find accepted terms, related examples, and business-rule owners.
2. Find each context with specified term information and controlling rules.
3. Find term relations, identifiers, and task owners at the boundaries of these contexts.
4. If term or rule decisions have effects on correctness, get missing decisions before work that uses them.
   Use [specification review](spec-review.md) for this decision.
5. Keep term and model proposals with their proposal status and accepted domain rules with their acceptance status.

A business context is a scope with term information that agrees and rule ownership.
Frontend and backend are software components.
Different component directories are not sufficient evidence of a business context map.
One component can operate in more than one business context.
More than one component can operate in one context.
When you examine proposals for domain models from AI, use accepted terms.

Names that are almost the same are not sufficient evidence that the terms are equivalent.

Example: Billing's Account is a billable customer relationship.
Identity's Account is a login principal.
Their accepted contract gives a customer ID relation for these terms.
Give the information for these terms and this customer ID relation in the record.
Do not give the two contexts the same term information only because they use the name Account.
A changed customer relation stays a proposal until acceptance with project approval.

## Select only necessary model tactics

Give important invariants: conditions with which accepted behavior must always agree.
Find the actor or component that must update the state and the necessary consistency of these updates.
When project terms and structures give these conditions, use them.

| Condition | Optional tactic |
| --- | --- |
| Identity stays the same while attributes change | An entity can keep this identity. |
| Attributes give value semantics | A value object can keep validation and value equality in one group. |
| State changes have accepted preconditions and outcomes | Transitions with specified preconditions and outcomes can make state behavior agree with its rules. |
| More than one update must keep one invariant together | An aggregate or transaction boundary can have the role for consistency. |

If a tactic corrects an identity, value, state, invariant, or consistency problem in this task, select it.
For other problems, these tactics are not necessary.
The same vocabulary is not sufficient evidence of transactional consistency.
When updates occur in different consistency scopes, record accepted time intervals, reconciliation, or failure behavior.
Microservices, CQRS, event sourcing, events, repositories, and specified folder layers are not mandatory.
When accepted rules make no more model tactics necessary, keep scripts and CRUD without added model tactics.

## Keep accepted boundaries when checks help

If coupling causes a risk of boundary violation again, examine checks that are available in the project.
Architecture tests or static analysis can examine dependencies, imports, or data access that do not agree with accepted boundaries.
Get these checks from accepted boundaries.
Do not make a new layer rule only because a tool can examine it.
Record the boundary that you examined and the conditions for which the method gives evidence.
Satisfactory results from architecture checks are not sufficient evidence of correct business behavior or full workflow acceptance.

Use [testing guidance](testing.md) for accepted invariants, compatible interfaces, and necessary effects.
