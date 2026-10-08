# Specification Quality and Coverage

## Review the intended behavior

Read the source request, accepted specification, interface contracts, and relevant project principles.
Separate intended behavior from observations of existing code.
Do not treat a working example as authority for a conflicting contract.

Check these dimensions for the current scope:

- Goal: identify the user outcome, scope, and non-goals.
- Precision: define inputs, outputs, units, defaults, limits, and relevant timing.
- Scenarios: cover normal behavior, boundaries, and relevant failure or recovery behavior.
- Consistency: compare related requirements, interfaces, terms, and versions.
- Assumptions: identify unsupported facts, missing dependencies, and choices that affect correctness.
- Constraints: check applicable compatibility and project principles. Record relevant non-functional acceptance conditions when necessary.

If accepted contracts conflict, identify the responsible authority and the exact conflict.
Resolve correctness-critical choices before dependent implementation or acceptance.
Use existing decisions and authorization when they resolve the issue.
Ask only about necessary choices that available records cannot resolve.
Continue independent investigation or an explicitly isolated prototype when useful.
Do not silently select a contract or weaken a requirement to match code.

Record other assumptions with their impact and validation method.
Do not require all uncertainty to disappear before independent work can continue.
Keep review depth proportional to the change.

## Select meaningful validation

Use concrete examples when a rule permits incompatible interpretations.
Identify the accepted rule, a distinguishing example, and any unresolved question.
State the relevant preconditions, input, and expected observable result.
Choose an example that distinguishes accepted behavior from a plausible incorrect result.
Use accepted rules or suitable reference results as the basis for expected values.

Review important test assertions, not only requirement links or test names.
A test that repeats an implementation mistake does not establish acceptance.
Check whether the assertions can detect the relevant failure.
Use counterexamples or an established independent reference when useful.

For test cycles, characterization, conditional broader checks, and test integrity, use [testing guidance](testing.md).
For context meanings, business-rule ownership, invariants, or consistency choices, use [domain guidance](domain.md).
Select the next useful detailed case from uncertainty and actual results. Do not require all speculative tests upfront.

Select checks from affected behavior and risk, not task size alone.
Use necessary integration or end-to-end checks for affected user workflows.
If dependencies are simulated, state what those simulations cannot establish.
If performance matters, record the workload, environment, statistic, limit, and observation period.
For security-sensitive changes, check relevant access and data boundaries.

For persisted data or configuration changes, check compatibility across affected versions.
Record failure detection and an authorized recovery path when operational risk requires them.
Restoring a previous binary does not necessarily restore previous data.

Keep small, low-impact checks brief.
Do not require every test type, formal notation, or a separate validation document.
Do not run production experiments or load tests without the necessary authorization.

## Trace requirements

Start from source requirements, not only the agent's derived task list.
Reuse existing requirement IDs, headings, issue references, or source links.
For each in-scope requirement, connect these items:

1. The source requirement and accepted intent.
2. Observable acceptance conditions and relevant scenarios.
3. The responsible task or necessary design decision.
4. The actual implementation location or artifact.
5. Applicable evidence and its current result.

For a small task, keep these references inline in the existing record.
For a larger change, use a coverage table:

| Source requirement | Acceptance condition | Task or decision | Implementation | Evidence and applicability | Gap or disposition |
| --- | --- | --- | --- | --- | --- |

Use the table only when it helps find omissions.
Do not create a parallel requirement catalog or impose a new identifier scheme.
Do not invent links, implemented behavior, or evidence to fill empty cells.

Check both directions:

- From requirements, find missing conditions, work, implementation, or evidence.
- From actual changes, find their requirement or necessary implementation reason.

Flag added behavior that lacks an accepted basis.
For excluded or deferred scope, record the source, impact, and project-authorized disposition.
Do not hide a required condition by removing its coverage row.

## Check requirement change operations

Use the project's existing delta format, identity links, or explicit accepted change description.
Do not require another schema or requirement catalog.

| Accepted operation | Necessary behavior check |
| --- | --- |
| Add | Check the new behavior and relevant interactions with existing behavior. |
| Modify | Check the changed conditions and behavior that remains required. |
| Remove | Check absence of the obsolete behavior, including remaining executable paths. |
| Rename | Follow the old and new identity. Check preserved behavior unless an accepted modification changes it. |

For removal, inspect affected callers, tests, configuration, generated files, and persisted data when relevant.
Accepted deprecation or migration can require a temporary compatibility path.
Record its accepted scope and end condition. Do not invent a transition to retain removed behavior.
An old positive test can be obsolete evidence after accepted removal.
Update affected assertions through the accepted change, rather than preserving a contradictory expectation.
Renaming a requirement does not require renaming implementation symbols unless the accepted contract specifies that change.
Check transitions and migration by risk. Do not require a migration document for a harmless name change.

## Review before acceptance

Check completeness, correctness, and consistency against the current candidate.
Read actual specifications, changes, and evidence.
For material risk, use available controlled acceptance procedures. Confirm actual controls before claiming enforced independence or permissions.
Distinguish implementation completion from complete acceptance.
For evidence requirements and verdicts, read [delivery instructions](delivery.md).
For accepted specification changes, follow [the workflow](workflow.md).
