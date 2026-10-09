# Business-System Project Prompts

Use these prompts for a business application with domain workflows and persisted state.
For selection and composition, read [project profiles](../../references/project-profiles.md).
Write information for the related prompts in the record that the project uses.
Keep its format and authority.

## Specification prompts

For the related prompts, use these instructions:

- Give domain terms and the accepted business outcome.
- Identify the roles from the business contract and their permitted actions.
- Give related states, transitions, and invalid transitions.
- Give data invariants, ownership, and necessary consistency boundaries.
- Identify the components that the system uses, their callers, and their interface contracts.
- Give inputs, outputs, error behavior, and compatibility requirements at these boundaries.
- If persisted data changes, give migration and recovery requirements.
- If runtime operations change, give necessary rollout, observation, and recovery requirements during operation.

Keep the accepted architecture.
If the system has a monolith, keep it in the accepted architecture.
Use the component boundaries that the system has.
Do not add layers, services, or a new framework as requirements.
For important domain ambiguity, use [domain guidance](../../references/domain.md).

## Acceptance example

For this example, the accepted purchase contract lets an approver give approval for an order in the pending state.
Approval makes one stock reservation and changes the order state to approved.
A subsequent approval attempt gives the same accepted result without a second reservation.
A user without the approver role gets the specified rejection.
After this rejection, the order and stock do not change.

The vertical check starts at the application request entry.
It examines authorization, domain behavior, and persisted state in this flow.
For each step in this example, a service only for the step is not necessary.
The roles and reservation rule become requirements only if the project accepts them in its contract.

## Conditional harness checks

For applicable checks, use these instructions:

- For changed business behavior, do a check of a full vertical flow through the components that the application uses.
- Do checks of accepted state transitions, related invalid transitions, and data invariants.
- If roles have an effect for the flow, compare permitted and rejected actions with state from execution.
- If component contracts change, do checks of consumer and provider components at the related boundaries.
- For concurrent actions that can cause an invariant failure, do a check of these concurrent actions.
  Also examine the state after these actions.
- If migration is applicable, do checks with typical data from before migration.
  Also examine the state after transformation and the accepted recovery behavior.
- If deployment changes, do checks of necessary operations in the accepted target environment.
- If reports or analysis help give the outcome, add only related [data-analysis prompts](data-analysis.md).

Checks of isolated components do not show the full business outcome.
Mocks at component boundaries do not show compatibility with the dependencies in the application.

In the evidence record that the project uses, record:
- The candidate
- The contract
- The environment
- State from the checks
- Remaining gaps.
