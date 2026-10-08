# Agent Project Prompts

Use these prompts for an agent that acts toward an accepted goal.
For selection and composition, read [project profiles](../../references/project-profiles.md).
Fill relevant prompts in the existing record. Keep its format and authority.

## Specification prompts

- State the accepted goal, observable outcome, and excluded work.
- Define allowed autonomous actions, tools, data access, and consequential side effects.
- Define necessary approval points through existing authority rules.
- Define budget, stop conditions, failure reporting, and recovery behavior.
- Identify which limits the host enforces and which remain written instructions.
- Identify durable context needed to continue after context loss or interruption.
- Define saved task state, completed effects, unresolved work, and the next action.
- If delegation helps, define bounded responsibilities and acceptance of returned results.

Independent execution remains the default.
Delegation is optional. No fixed agent team or distributed coordinator is required.
For required controls, check actual host support before dependent work.

## Acceptance example

Suppose the accepted task creates `summary.md` from a permitted local document set.
The agent may write that artifact but may not send messages or publish it.
An interruption occurs after it writes part of the summary.
The resumed agent reads saved task state and checks the actual artifact.
It completes the accepted summary without duplicating completed external effects.
The acceptance check examines the summary, relevant tool effects, and truthful completion report.

An example budget can bound tool calls or elapsed time.
Before relying on a hard budget control, identify available native enforcement.

## Conditional harness checks

- For deterministic components, check useful rules such as output paths, schemas, calculations, and stop transitions.
- For agent behavior, run representative tasks against observable artifacts and actual side effects.
- For model behavior acceptance, repeat bounded trials under declared inputs and execution conditions.
- Before model trials, state their count, failure allowance, and acceptance threshold.
- After model trials, record observed variation and its effect on acceptance.
- If stop conditions apply, check actual stopping behavior and the reported unfinished work.
- If recovery applies, interrupt execution and check saved state against actual completed effects.
- If tools can cause external effects, check their applicable authorization and uncertain completion handling.
- If delegation applies, check combined task outcomes and disposition of failed or incomplete results.

Keep deterministic evidence and model trial evidence distinct.
One successful response does not establish reliable task completion.
Written budgets do not enforce tool restrictions, elapsed time, or spending limits.
Record available enforcement, missing controls, actual results, and variance limits in the existing evidence record.
