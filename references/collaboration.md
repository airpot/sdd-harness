# Optional Collaboration and Local Chats

## Keep independent development simple

Independent development is the default.
Use the existing specification, task record, commands, and handoff location.
For a small correction, keep brief acceptance and evidence references in that record.
Do not require frontend/backend task splits, role profiles, new contract formats, mocks, or team CI setup for independent work.

Use the following procedures only when tasks need cooperation or chats share project resources.
Apply [the writing policy](writing.md) to new and changed internal prose.

## Divide work through accepted boundaries

For one repository, retain the existing directory structure and task tracker.
Link each component task to the overall requirement and complete business outcome.
Record its responsible developer, scope, dependencies, accepted contract reference, deliverable, and relevant acceptance conditions.
Identify the existing integration duty and target. One person can perform several duties.

For example, order submission needs both persistence and the correct visible result.
A frontend task can cover submission and display. A backend task can cover validation and persistence.
Separate component passes do not establish that the complete order workflow works.

Use explicit task assignments and ordinary Git branches or independent checkouts for separate work.
Do not require cross-machine claims, heartbeat leases, or a coordination service before starting independent assigned tasks.
If scope or ownership conflicts, resolve the affected boundary before conflicting writes.
Continue work that does not depend on that resolution.

## Use one accepted contract

Find the existing authoritative interface contract and its accepted version or commit.
Keep its location and format. OpenAPI is optional.
Identify proposals and stale examples separately from accepted behavior.

Check the contract details that affect the task:

- Requests, responses, field names, required fields, optional fields, and null behavior.
- Errors, access rules, pagination, time formats, time zones, and units.
- Linked business rules, observable effects, and useful examples.

Bind mocks and generated clients to the contract version they implement.
Compare their behavior with the accepted contract. Correct stale fixtures and consumer assumptions.
If the contract changes, review affected generated files, examples, and earlier evidence.
Do not create another authoritative copy merely to support this skill.

## Check the actual combination

Record component evidence separately from evidence for the complete workflow.
A frontend result with a mock can establish only the behavior that the mock checks.
Before complete acceptance, obtain applicable evidence from the actual provider and consumer combination.
Check relevant request validation, authentication, errors, empty results, and accepted business effects.
Schema checks alone do not establish business behavior or access enforcement.
Keep required checks that failed, did not run, or remain blocked visible.

Construct one exact combined candidate against the current integration target.
Reference its accepted contract version, necessary configuration, input data, and repeatable check commands.
Validate the complete required workflow on that candidate.
Review evidence applicability after relevant target, contract, dependency, or environment changes.
Independent branch success does not authorize selection of the newest branch for release.
Use [delivery rules](delivery.md) for authorized publication of the selected candidate.

## Change shared behavior deliberately

For contract, shared type, configuration, or schema changes, identify affected tasks and callers.
Record the proposed behavior, compatibility impact, and necessary migration or transition.
Keep unaccepted changes as proposals. Follow existing project acceptance authority before dependent implementation.
Coordinate affected task updates and relevant validation before accepting the combination.

Use an additive transition when compatibility requires one.
Preserve original evidence and defect reproduction. Do not silently change expected results to fit the proposal.

## Reference project harness settings

Use existing project instructions, component READMEs, task records, and supported host settings.
For a cooperating task, retain only the references needed to run and check its scope.

| Setting | Necessary reference |
| --- | --- |
| Project entry | Existing specification, task tracker, instructions, and writing policy. |
| Task boundary | Assigned scope, relevant paths, dependencies, and integration duty. |
| Shared contract | Accepted location and exact version; related examples or generated clients. |
| Workspace | Independent checkout or worktree, branch, and actual activity observations. |
| Runtime resources | Relevant ports, databases, containers, logs, and isolated test data. |
| Checks | Actual component and combined commands, setup, inputs, pass criteria, and logs. |
| Integration | Current target and exact combined candidate. |
| Permission evidence | Observed native permissions, hooks, review rules, and release entry when applicable. |

These are record references, not a new native configuration schema.
Do not invent host configuration keys or successful check results.
Written path scopes instruct agents. They do not enforce filesystem permissions.

Check actual host or repository controls before claiming enforcement.
CODEOWNERS alone does not prove both parties must approve or that writes are restricted.
Use existing Git and CI controls within authorization. Do not require new CI infrastructure merely to use this skill.
Do not change global agent configuration to force these settings.

## Protect local work and handoffs

Before writing, identify the repository, checkout, branch, task owner, active chats, and background tasks.
The bundled `inspect` command observes Git only. Unknown activity does not mean idle.
A clean Git status or a closed window does not prove that writers stopped.
If a chat enters a busy worktree, use a fixed snapshot or a separate worktree.
Do not commit, clean, or publish from the original checkout without authority.

Isolate conflicting ports, databases, containers, and logs. A worktree isolates files only.

For a planned handoff, save results and evidence before the original executor stops writing.
Before transferring responsibility, confirm that the original writers stopped.
The next executor must check current ownership and actual state before continuing.

After a disconnection, identify missing results from the latest accessible checkpoint.
If stopped state is uncertain, continue independent work in a separate checkout.
If an earlier executor returns, check the current task assignment before writing.
Task records do not stop processes or grant release authority.

Use ordinary Git for portable code results.
Transfer necessary artifacts to authorized storage with checksums and recovery steps.
Check received results. Do not transfer credentials by default.
Use [recovery rules](recovery.md) before removing worktrees.

## Use different agents

Use the same instruction version when developers cooperate.
Read [installation instructions](install.md) for actual discovery locations.
Check each host's tools, permissions, and hooks. Similar event names do not prove equivalent behavior.
If automatic loading is unavailable, invoke the skill explicitly.

If necessary, add a short entry to existing project instructions. Preserve their existing content.
Keep development, integration, release authorization, and native enforcement distinct.
