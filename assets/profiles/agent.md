# Agent Project Prompts

Use these prompts for an agent that does work for an accepted goal.
For selection and composition, read [project profiles](../../references/project-profiles.md).
Write information for the related prompts in the record that the project uses.
Keep its format and authority.

## Specification prompts

For the related prompts, use these instructions:

- Give the accepted goal, observable outcome, and work that the task does not include.
- Give permitted autonomous actions, tools, data access, and side effects that can be important.
- Give necessary approval points in the authority rules that the project uses.
- Give the budget, stop conditions, failure reports, and recovery behavior.
- Identify the limits with host enforcement and the limits that are only written instructions.
- Identify the context to keep for continuation after context loss or interruption.
- Give the recorded task state, completed effects, work without a resolution, and the next action.
- If delegation helps, give responsibilities with specified limits and acceptance of the results that the subagents give.

The default is work that the agent does independently.
Delegation is optional.
An agent team that must keep the same composition is not necessary.
A distributed coordinator is not necessary.

Before work for which a control is necessary, make sure that the host has the control.

## Acceptance example

For this example, the accepted task makes `summary.md` from a permitted set of local documents.
The agent can write the artifact, but it is not permitted to send messages or publish the artifact.
An interruption occurs after the agent writes part of the summary.
After the interruption, the agent reads the recorded task state and examines the artifact.
It completes the accepted summary and does not cause the completed external effects again.
The acceptance check examines the summary, related tool effects, and a completion report that agrees with the evidence.

An example budget can give limits for tool calls or elapsed time.

Before you use a hard budget control, identify the enforcement that the host supplies.

## Conditional harness checks

For applicable checks, use these instructions:

- For deterministic components, do checks of rules that help.
  For example, do checks of output paths, schemas, calculations, and stop transitions.
- For agent behavior, do typical tasks. Then, examine their artifacts and side effects from execution.
- For acceptance of model behavior, do trials again with specified limits, inputs, and execution conditions.
- Before model trials, give their count, failure allowance, and acceptance threshold.
- After model trials, record the variation that you found and its effect for acceptance.
- If stop conditions are applicable, examine behavior when the agent stops.
  Also examine the report about work that is not completed.
- If recovery is applicable, make an interruption occur during execution.
  Then, compare the recorded state with the completed effects from execution.
- If tools can cause external effects, examine their applicable authorization and recovery for completion with an unknown outcome.
- If delegation is applicable, examine task outcomes in combination. Also examine dispositions of results that are not satisfactory or not completed.

Record evidence from deterministic checks and model trials in different groups.

One satisfactory response does not show reliability for task completion.
Written budgets are not controls for tool restrictions, elapsed time, or spending limits.

In the evidence record that the project uses, record:
- Available enforcement
- Missing controls
- Execution results
- Variance limits.
