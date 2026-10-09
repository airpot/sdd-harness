# Specification Quality and Coverage

## Examine accepted behavior

Read the source request, accepted specification, interface contracts, and related project principles.
Keep the source and acceptance status for accepted behavior.
Keep the source and acceptance status for code observations.
Do not use an example that operates correctly as approval for a contract that does not agree with it.

Examine these items for this scope:

- Task: find the user outcome, scope, and outcomes not in this task.
- Precision: give inputs, outputs, units, defaults, limits, and related timing.
- Scenarios: include usual behavior, boundaries, and related failure or recovery behavior.
- Consistency: compare related requirements, interfaces, terms, and versions.
- Facts without evidence: find missing dependencies and all decisions with effects on correctness.
- Constraints: examine applicable compatibility and project principles.
  If acceptance conditions for non-functional behavior are necessary, record the related conditions.

If accepted contracts are in conflict, find the conflict in the source contracts.
Find who must give the decision with project approval.
If correctness makes a decision necessary, get it before implementation or acceptance that uses it.
If project decisions and approval give this decision, use them.

For necessary decisions that available records cannot give, get user decisions.
If investigation helps the task, continue it independently.
If a prototype helps the task, continue it in its specified boundaries.
Use available controls or different resource instances to prevent conflicts.
Do not select a contract without a report of the cause or decrease a requirement only to agree with code.

Record other facts without evidence with their effects and validation method.
Work that you do independently can continue without decisions for all conditions without sufficient evidence.
Use the change's scope and effects to select review scope and procedures.

## Select checks that give acceptance evidence

When a rule can give results that are not compatible, use examples with specified inputs and results.
Find the accepted rule, an example that shows the difference, and each missing decision.
Give related preconditions, input, and the expected result that you can see.
Select an example that shows different results for accepted behavior and possible incorrect behavior.
Get expected values from accepted rules or applicable reference results.

Examine important test assertions directly.
Requirement links and test names are not sufficient.
A test that has the same error as implementation is not sufficient evidence of acceptance.
Make sure that assertions can find the related failure.

If counterexamples help the task, use them.
If a reference helps the task, use it for acceptance.
The reference must have sufficient evidence from a source other than the candidate.

For test cycles, characterization, test integrity, and more checks necessary for the task, use [testing guidance](testing.md).
For business terms, business-rule ownership, invariants, or consistency decisions, use [domain guidance](domain.md).
Use information without sufficient evidence and results from execution to select the next case with specified inputs and results.
All possible tests with fully specified cases are not necessary before you examine results from previous cases.

Select checks from behavior with effects from the change and risk, not only task size.
Use necessary integration or end-to-end checks for user workflows with effects from the change.
If dependencies are simulated, give the behavior for which these simulations cannot supply evidence.
If performance is important, record the workload, environment, statistic, limit, and observation period.
For changes with effects on security, examine related access and data boundaries.

For stored data or configuration changes, examine compatibility for versions with effects from the change.
When risk from operation makes failure checks and recovery necessary, record the checks and permitted recovery path.
A previous binary after recovery is not sufficient evidence that data agrees with its previous state.

Keep small checks with small effects short.
Select the test types necessary for the task.
All test types, formal notation, and an added validation document are not mandatory for each task.
Do not do production experiments or load tests without necessary authorization.

## Give references from requirements to evidence

Start from source requirements, not only the task list from the agent.
Use requirement IDs, headings, issue references, or source links that the project has.
For each requirement in scope, give references for these items:

1. The source requirement and accepted behavior
2. Acceptance conditions that checks can examine and related scenarios
3. The task owner or necessary design decision
4. The implementation location or artifact directly
5. Applicable evidence and its result at this time.

For a small task, keep these references inline in the record that the project uses.
For a larger change, use a coverage table:

| Source requirement | Acceptance condition | Task or decision | Implementation | Evidence and applicable conditions | Missing work or decision |
| --- | --- | --- | --- | --- | --- |

If the table helps find omissions, use it.
For other work, the table is not necessary.
Do not make one more requirement catalog or a mandatory new format for identifiers.
Do not write links, behavior from code, or evidence in empty cells without a source.

Do these two checks:

- From requirements, find missing conditions, work, implementation, or evidence.
- From source changes, find their requirement or the source that makes their implementation necessary.

Give a report of added behavior without an accepted source.
For scope not included or without a decision, record the source, effects, and permitted decision with project approval.
Do not remove a coverage row to make a necessary condition not available to the reader.

## Examine requirement change operations

Use the project's delta format, identity links, or an accepted change description that gives the operation.
One more schema or requirement catalog is not necessary.

| Accepted operation | Necessary behavior check |
| --- | --- |
| Add | Examine the new behavior and related interactions with behavior that the project has. |
| Modify | Examine changed conditions and behavior that continues to be necessary. |
| Remove | Examine if there is no behavior that the accepted change removes. Include executable paths that the project continues to have. |
| Rename | Find previous and new identities and their references. If an accepted change does not change the behavior, keep the behavior the same. |

For removal, examine related callers, tests, configuration, generated files, and stored data with effects from the removal.
Accepted deprecation or migration can make a temporary compatibility path necessary.
Record its accepted scope and end condition.
Without an accepted source, do not make a transition to keep removed behavior.
After accepted removal, a previous test with a satisfactory result can become evidence that is not applicable.

Use the accepted change to change assertions with effects from this change.
Do not keep expected results that do not agree with accepted behavior.
A requirement rename makes no implementation symbol rename necessary unless the accepted contract gives this change.
Use risk to select transition and migration checks.
A migration document is not necessary for a name change without unwanted effects.

## Examine before acceptance

Examine completeness, correctness, and consistency for the candidate at acceptance.
Read source specifications, changes, and evidence directly.
Before you give a report of independence or permissions from native controls, examine the controls in use directly.
Before you give a report of independence or permissions from native controls, examine controls directly.
Keep the source and scope for task status.
Keep the source and scope for acceptance status.

For evidence requirements and verdicts, read [delivery instructions](delivery.md).
For accepted specification changes, obey [the workflow](workflow.md).
