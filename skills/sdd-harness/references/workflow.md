# From Specification to Acceptance

## Use project records

Find the OpenSpec, Spec Kit, or custom specification entry that the project actually uses.
Reference its requirements, decisions, and tasks. Do not require a new directory structure.

If records are missing, keep a short goal, acceptance conditions, and a handoff record for a simple task.
For a change with multiple steps, use the [change template](../assets/change.md) at the project's existing location.
If the project has no location, use `.sdd-harness/changes/<change-id>.md`.
Remove fields that do not apply.
For new or changed internal prose, follow [the writing policy](writing.md).

For a new project, select one feature with observable acceptance conditions.
For an existing system, record relevant behavior and known failures.
Identify the behavior to change and the compatibility boundaries to keep.

## Clarify and plan

Resolve choices that affect implementation or acceptance.
Check available facts before asking the user.
Ask only about necessary choices that the records cannot resolve and you cannot reasonably infer.
A new chat or agent does not cancel existing authorization.

Before dependent work, use [specification review](spec-review.md) to identify conflicts, assumptions, and missing scenarios.
Trace source requirements through acceptance conditions, tasks, actual changes, and evidence.
Use inline references for small tasks. Use a coverage table only when useful.

Write observable acceptance conditions.
For example: "With default pagination, existing callers retrieve all items without duplicates or omissions."
Do not use "Implement pagination" as an acceptance condition.
If relevant, specify inputs, time, environment, and expected results.

Split tasks to reduce interface conflicts.
Use accepted interfaces for parallel work.
Before accepting combined results, obtain the actual dependencies.
Then check the combination.
Changes to shared contracts affect related tasks even when their files differ.

## Implement and check

For each batch, read the actual diff.
Check ownership, duplicate implementations, temporary compatibility changes, and new dependencies.
Do not include another task's results in a commit without coordination.
If changes have unknown ownership, preserve those changes.
Then identify their owner. Do not discard the changes.

Select checks that examine the required behavior.
Record the exact code or snapshot, specification version, method, environment, result, and log location.
Define the method as an executable command or repeatable observation procedure.
Record necessary input versions, setup, and the expected result or pass criterion.
Use authorized references for sensitive inputs. Do not copy credentials into records.
List baseline failures separately. State whether each baseline failure relates to the change.
Keep checks that did not run visible.

If behavior, specifications, dependencies, or environments change, review the applicable evidence again.
Record whether each relevant result applies, does not apply, or remains unassessed.
Record the reason and covered acceptance conditions when carrying evidence forward.
Keep original records.
For review, read the specifications, diffs, and evidence directly.
Agreement between models does not replace actual checks.

For deferred issues, record the impact, responsible task or owner, resolution condition, and effect on acceptance.
Do not skip a necessary requirement by calling it technical debt.

## Reconcile accepted changes

Identify the project's authoritative specification and maintenance convention.
Do not assume that every feature document is a living contract.

- For living specifications, update the accepted behavior in the current contract.
- For historical feature records, keep old documents intact. Record explicit extension or superseding links and the current behavior reference.
- If implementation reveals a new behavior choice, record a proposal before treating it as accepted intent.

Use existing project authority and user authorization for accepted updates.
Do not ask for repeated approval of an already accepted change.
Update affected plans, task references, interfaces, and coverage when necessary.
Preserve important design reasons and original evidence.

Before complete acceptance, verify that authoritative records describe the accepted candidate consistently.
If reconciliation is pending, record the gap and its effect on acceptance.
An unchanged specification needs no rewrite merely to complete a small correction.

## Save checkpoints

Update the task handoff record when recoverable results, important decisions, handoffs, or validation conclusions change.
Do not log every tool call.
Save results and evidence references instead of copying the complete chat into the next context.
