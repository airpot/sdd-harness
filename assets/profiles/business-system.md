# Business-System Project Prompts

Use these prompts for a business application with domain workflows and persisted state.
For selection and composition, read [project profiles](../../references/project-profiles.md).
Fill relevant prompts in the existing record. Keep its format and authority.

## Specification prompts

- Define domain terms and the accepted business outcome.
- Identify actual roles and their permitted actions.
- Define relevant states, transitions, and invalid transitions.
- Define data invariants, ownership, and required consistency boundaries.
- Identify existing components, callers, and actual interface contracts.
- Define inputs, outputs, error behavior, and compatibility requirements at those boundaries.
- If persisted data changes, define migration and recovery requirements.
- If runtime operations change, define necessary rollout, observation, and operational recovery requirements.

Preserve the accepted architecture, including an existing monolith.
Use actual component boundaries. Do not impose layers, services, or a new framework.
For significant domain ambiguity, use [domain guidance](../../references/domain.md).

## Acceptance example

Suppose the accepted purchase contract permits an approver to approve a pending order.
Approval creates one stock reservation and changes the order state to approved.
A later approval attempt returns the accepted existing result without another reservation.
A user without the approver role receives the defined rejection.
The order and stock remain unchanged after that rejection.

The vertical check follows the real request entry through authorization, domain behavior, and persisted state.
The example does not require a separate service for any step.
Its roles and reservation rule become requirements only through the project's accepted contract.

## Conditional harness checks

- For changed business behavior, check a complete vertical flow through the actual components.
- Check accepted state transitions, relevant invalid transitions, and data invariants.
- If roles affect the flow, check permitted and rejected actions against actual state.
- If component contracts change, check actual consumers and providers at the affected boundary.
- If concurrent actions threaten an invariant, check the relevant competing actions and final state.
- If migration applies, check representative old data, the transformed state, and accepted recovery behavior.
- If deployment changes, check required operations in the accepted target environment.
- If reports or analysis support the outcome, add only relevant [data-analysis prompts](data-analysis.md).

Isolated component checks do not establish the complete business outcome.
Mocked boundaries do not prove compatibility with actual dependencies.
Record the candidate, contract, environment, observed state, and remaining gaps in the existing evidence record.
