# Optional Project Profiles

A profile supplies specification prompts and checks for a deliverable type.
The primary profile matches the accepted main outcome.
Profiles add relevant details to the common SDD workflow.

For a narrow change, keep the entry's short independent path.
Independent development remains the default.
Profile selection requires no new stack, scaffold, team, worktree, or distributed coordination.

## Select by the actual deliverable

1. Identify the accepted outcome, existing authoritative record, and current architecture.
2. If a profile fits the actual deliverable, select it as the primary profile.
3. If the outcome needs another capability, select only its applicable prompts and checks.
4. If none fits, use the [general change workflow](workflow.md) without forcing a profile.

| Actual deliverable | Optional prompts |
| --- | --- |
| Reusable agent instructions with portable resources | [Skill](../assets/profiles/skill.md) |
| An MCP server or exposed MCP capability | [MCP](../assets/profiles/mcp.md) |
| An agent that acts toward an accepted goal | [Agent](../assets/profiles/agent.md) |
| A business application with domain workflows and persisted state | [Business system](../assets/profiles/business-system.md) |
| A report, analysis, model, or repeatable data transformation | [Data analysis](../assets/profiles/data-analysis.md) |

A report inside a business application can need business-system and data-analysis prompts.
An agent that produces analysis can need agent and data-analysis prompts.
These combinations do not require two development flows.

## Compose in the existing record

1. Record the primary profile and relevant additions in the existing task or specification record.
2. Fill only prompts that affect accepted behavior or necessary evidence.
3. Merge overlapping terms, contracts, and checks in that record.
4. Before dependent work, resolve compatibility and authority conflicts across selected capabilities.
5. Remove inapplicable sections.
6. Keep the existing format and authoritative record.

If a conflict remains unresolved, continue work that does not depend on it.
Preserve accepted architecture and valid existing authorization.
Do not create a second authoritative specification or global configuration for a profile.

The templates are optional prompts, not required documents.
Examples illustrate possible contracts. They do not set project policy.
Before saving a record, check its links from the actual destination.
Do not copy resource links or policy placeholders that the next reader cannot resolve.
For new internal prose, apply the [writing policy](writing.md).

## Select evidence by applicability

Use the selected prompts to state observable acceptance conditions.
Choose checks for the actual contracts, artifacts, side effects, and environment.
Keep static validity, deterministic behavior, and model behavior evidence distinct.
For necessary checks, use [testing guidance](testing.md) and [specification review](spec-review.md).

Profile instructions do not confer permissions.
Written limits do not enforce host permissions or runtime controls.
For required controls, check actual host capabilities through [installation guidance](install.md).
If a required check cannot run, retain its acceptance gap and next action.
