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
State the relevant preconditions, input, and expected observable result.
Choose an example that distinguishes accepted behavior from a plausible incorrect result.
Use accepted rules or suitable reference results as the basis for expected values.

Review important test assertions, not only requirement links or test names.
A test that repeats an implementation mistake does not establish acceptance.
Check whether the assertions can detect the relevant failure.
Use counterexamples or an established independent reference when useful.

Use property, differential, or mutation checks only when their value justifies their cost.
For randomized checks, retain necessary seeds and failing inputs for reproduction.
Passing sampled inputs provide evidence. They do not prove behavior for every possible input.

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

## Review before acceptance

Check completeness, correctness, and consistency against the current candidate.
Read actual specifications, changes, and evidence.
Distinguish implementation completion from complete acceptance.
For evidence requirements and verdicts, read [delivery instructions](delivery.md).
For accepted specification changes, follow [the workflow](workflow.md).
