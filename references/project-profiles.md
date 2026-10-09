# Optional Project Profiles

A profile supplies specification prompts and checks for a deliverable type.
The primary profile agrees with the accepted primary outcome.
All profiles use the SDD workflow.
They add related information to it.

For a change with a small scope, keep the entry's short path for development work that you do independently.
As the default procedure, do development work independently.
Profile selection makes no new stack, scaffold, team, worktree, or distributed coordination necessary.

## Select a profile for the deliverable

To select a profile for the deliverable, do these steps:

1. Find the accepted outcome, record with project authority, and architecture that the project uses.
2. If a profile agrees with the deliverable, select it as the primary profile.
3. If one more capability is necessary for the outcome, select only its applicable prompts and checks.
4. If none agrees, use the [general change workflow](workflow.md).
   Do not make a profile mandatory.

| Deliverable | Optional prompts |
| --- | --- |
| Agent instructions that you can use again with portable resources | [Skill](../assets/profiles/skill.md) |
| An MCP server or MCP capability available to clients | [MCP](../assets/profiles/mcp.md) |
| An agent that does work to complete an accepted goal | [Agent](../assets/profiles/agent.md) |
| A business application with domain workflows and state that is kept in storage | [Business system](../assets/profiles/business-system.md) |
| A report, analysis, model, or data transformation that you can do again | [Data analysis](../assets/profiles/data-analysis.md) |

A report in a business application can make business-system and data-analysis prompts necessary.
An agent that supplies analysis can make agent and data-analysis prompts necessary.
These combinations do not make two development workflows necessary.

## Put profiles in the project's record

To put profiles in the project's record, do these steps:

1. Record the primary profile and related added prompts and checks in the task or specification record that the project uses.
2. Write information for only prompts with effects on accepted behavior or necessary evidence.
3. Keep terms, contracts, and checks in this record.
   For parts with the same meaning and scope, keep one entry.
4. Before work that uses selected capabilities together, get decisions for their compatibility and authority conflicts.
5. Remove sections that are not applicable.
6. Keep the format and record with project authority that the project uses.

If a conflict has no decision, continue work that does not make this decision necessary.
Keep accepted architecture and previous authorization that continues to be applicable.
Do not make a second specification with authority or global configuration for a profile.

The templates are optional prompts.
They are not mandatory documents.
Examples show possible contracts.
They do not have project policy authority.
Before you keep a record, examine its links from the record's destination directory.
Do not make copies of resource links or policy placeholders that the next reader cannot use to find the target.

For new prose for project development, obey the [writing policy](writing.md).

## Select applicable evidence

Use the selected prompts to give acceptance conditions that checks can examine.
Select checks for the contracts, artifacts, side effects, and environment directly.
Keep evidence for static validity, deterministic behavior, and model behavior different.
For necessary checks, use [testing guidance](testing.md) and [specification review](spec-review.md).

Profile instructions do not give permissions.
Written instructions do not supply native controls for host permissions or runtime actions.
For necessary controls, examine host capabilities with [installation guidance](install.md).
If a necessary check cannot run, keep its condition without acceptance and next step.
