# Optional Collaboration and Local Chats

## Do development work independently

As the default procedure, do development work independently.
Use the specification, task record, commands, and handoff location that the project uses.
For a small correction, keep short acceptance and evidence references in this record.
Frontend/backend task splits, role profiles, new contract formats, mocks, and team CI setup are not necessary for development work that you do independently.

If tasks must operate together or chats use shared project resources, use these procedures.
For other work, these procedures are not necessary.
Obey [the writing policy](writing.md) for new and changed prose for project development.
If a main agent gives work with a specified scope and conditions, read [subagent rules](subagents.md).
For development work that you do independently, subagents are optional.
Subagent tasks and developer task assignments are different.

## Divide work at accepted boundaries

For one repository, keep the directory structure and task tracker that the project uses.
Record references from each component task to the full requirement and business outcome.
Record its developer, scope, dependencies, accepted contract reference, deliverable, and related acceptance conditions.
Find the integration role and target that the project uses.
One person can have more than one role.

For example, order submission must keep the order in storage and show the correct result.
A frontend task can include submission and display.
A backend task can include validation and storage.
Component passes are not sufficient evidence that the full order workflow operates correctly.
Frontend/backend task boundaries do not give business contexts.
If terms or rules are different in different contexts, find rule owners and accepted translations in [domain guidance](domain.md).

Use task assignments that give scope and ownership.
Use Git branches or different checkouts for work that you do independently.
Cross-machine claims, heartbeat leases, and a coordination service are not necessary before you start your tasks independently.
If scopes or owners have a conflict, get a decision for the boundary in conflict before conflicting writes.
Continue work that does not make this decision necessary.

## Use one accepted contract

Find the interface contract that has project authority and its accepted version or commit.
Keep its location and format.
OpenAPI is optional.
Keep sources and acceptance status for proposals, examples that do not agree with the contract, and accepted behavior.

Examine the contract information with effects on the task:

- Requests, responses, field names, fields that are mandatory or optional, and null behavior
- Errors, access rules, pagination, time formats, time zones, and units
- Related business rules, effects that you can see, and examples that help the task.

Record the contract version that mocks and generated clients use for their behavior.
Compare their behavior with the accepted contract.
Correct fixtures and consumer information without sufficient evidence that does not agree with the contract.
If the contract changes, examine generated files, examples, and previous evidence with effects from this change.
Do not make one more copy with contract authority only to use this skill.

## Examine the combination

Keep component evidence and evidence for the full workflow in different groups.
A frontend result with a mock gives evidence only for behavior that the mock examines.
Before full acceptance, get applicable evidence from the provider and consumer combination in execution.
Do checks of related request validation, authentication, errors, empty results, and accepted business effects.
Schema checks are not sufficient evidence of correct business behavior or access enforcement.
Contract compatibility checks include only the requests, responses, errors, and versions that they examined.

Compare consumer requests with the provider's accepted behavior, not only response shapes that agree.
Do checks of necessary storage changes and other side effects in the full workflow.
Keep records of necessary checks with results that are not satisfactory, no execution, or blockers.

Make one combined candidate with the integration target at this time.
Record its commit or artifact hashes to identify this candidate.
Give references to its accepted contract version, necessary configuration, input data, and commands for checks that you can do again.
Do the checks for the full necessary workflow for this candidate.
After related target, contract, dependency, or environment changes, examine if the evidence is applicable.

Satisfactory results from branches that operate independently give no approval to select the newest branch for release.
Use [delivery rules](delivery.md) for permitted publication of the selected candidate.

## Change shared behavior

For contract, shared type, configuration, or schema changes, find tasks and callers with effects from this change.
Record the behavior in the change proposal, compatibility effects, and necessary migration or transition.
Keep changes without acceptance as proposals.
Before implementation that uses the proposal, obey the project's acceptance authority.
Before acceptance of the combination, do task coordination for updates with effects from the change and related validation.

If compatibility makes a transition necessary, use a transition that adds behavior before removal.
Keep initial evidence and defect reproduction.
Do not change expected results without a report of the cause to make them agree with the proposal.

## Give references to project harness settings

Use project instructions, component READMEs, task records, and host settings that are available.
For a task that must operate with other tasks, keep only references necessary to do and examine its work.

| Setting | Necessary reference |
| --- | --- |
| Project entry | Specification, task tracker, instructions, and writing policy that the project uses. |
| Task boundary | Scope from the task assignment, related paths, dependencies, and integration role. |
| Shared contract | Accepted location and version or commit. Related examples or generated clients. |
| Workspace | Checkout or worktree that operates independently, branch, and activity that you see. |
| Runtime resources | Give references to related ports, databases, containers, logs, and test data. Use available controls or different resource instances that prevent conflicts. |
| Checks | Component and combined commands, setup, inputs, pass criteria, and logs from the checks. |
| Integration | Target at integration and identity of the combined candidate. |
| Permission evidence | If permission evidence is applicable, give the native permissions, hooks, review rules, and release entry that you examined. |

These are record references.
They do not give a new schema for native configuration.
Do not give host configuration keys without a host source.
Do not give check results without evidence from execution.

Written path scopes give instructions to agents.
They do not supply native controls for filesystem permissions.
For secrets that are not necessary, do not include them in model context.
Give references to inputs with access restrictions with permitted controls that the project uses.

Before you give a report of enforcement, examine the host or repository controls in use directly.
CODEOWNERS is not sufficient evidence that each party must give approval.
It is not sufficient evidence of controls that prevent writes.
Use Git and CI controls that the project uses, with authorization.
New CI infrastructure is not necessary only to use this skill.
Do not change global agent configuration to make these settings mandatory.

## Keep local work and handoffs

Before writes, find the repository, checkout, branch, task owner, active chats, and background tasks.
The skill's `inspect` command examines Git only.
Unknown activity is not evidence that no execution is active.
A clean Git status or a closed window is not sufficient evidence that writers stopped.
If a chat starts in a worktree with active writers, select one of these:

- A snapshot that does not change
- A different worktree.
Do not commit from the initial checkout without approval.
Do not use Git cleanup or publication from this checkout without approval.

Use available controls or different resource instances to prevent conflicts for ports, databases, containers, and logs.
A worktree keeps only files in a different directory.

Before a handoff and before the initial executor stops writes, keep results and evidence.
Before the next executor gets responsibility, make sure that the initial writers stopped.
Before the next executor continues, it must examine ownership and state at this time.

After a disconnection, find missing results from the last checkpoint that you can read.
If you do not know if writers stopped, continue work independently in a different checkout.
If a previous executor is available again, examine the task assignment at this time before writes.
Task records do not stop processes or give release authority.

Use Git for portable code results.
Move necessary artifacts to permitted storage with checksums and recovery steps.
Examine received results.
As the default procedure, keep credentials in their initial storage.
Use [recovery rules](recovery.md) before worktree removal.

## Use different agents

When developers operate together, use the same instruction version.
Read [installation instructions](install.md) for discovery locations that each host uses.
Examine each host's tools, permissions, and hooks.
Event names that are almost the same are not sufficient evidence of equivalent behavior.
If automatic invocation is not available, use the skill name for invocation.

If a skill entry is necessary, add a short entry to project instructions that the project uses.
Keep their content.
Keep the scope and controls for development, integration, release approval, and native enforcement.
