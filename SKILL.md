---
name: sdd-harness
description: Use when specification-driven development spans changes, chats, worktrees, developers, coding agents, or subagents. Use when resuming tasks, checking acceptance evidence, preparing releases, or recovering project worktrees.
metadata:
  version: "0.6.0"
---

# SDD Harness

Keep requirements, changes, evidence, and handoffs consistent.
Use the project's existing specifications, Git tools, and host tools.
Do not create a management platform to use this skill.

Independent development is the default. Use collaboration procedures only when the task needs cooperation.
For small tasks, keep brief references in existing records. Omit fields and setup that do not apply.

## Enter a project

1. Read the user goal, project instructions, specification entry, and relevant task handoff record.
2. Keep existing user authorization. Load only the material necessary for the task.
3. Before you change files, identify the repository, worktree, branch, changes, task owner, and active users.
4. If useful, run `inspect` for Git observations. Also check host chats, background tasks, and task ownership.
5. If the worktree is busy or its owner is unknown, use a fixed snapshot or a separate worktree.

A clean Git status, an expired heartbeat, or a closed window does not prove that a worktree is idle.
Resolve script paths from this skill directory to absolute paths.
Save project records in the target project. Do not save project records in the skill installation directory.

## Write internal documents

Use English and ASD-STE100 writing rules for internal development documents that you create or change.
Before you write these documents, read [references/writing.md](references/writing.md).
Apply the rules to specifications, plans, decisions, validation records, handoff records, and release or recovery records.

Keep source quotations, code identifiers, commands, paths, and raw evidence unchanged.
Follow explicit user language requests and mandatory project formats.
Use the user's language for conversation unless the user requests another language.
Do not translate unrelated existing documents.

## Develop a change

Use OpenSpec's accepted specifications and incremental changes.
Use Spec Kit's clarification, principle checks, and consistency analysis.
Both tools are optional.

- Find accepted requirements, relevant interfaces, and baseline behavior. Reference existing specifications and tasks instead of duplicating them.
- Define observable acceptance conditions, dependencies, and the next verifiable change. Keep small tasks brief.
- Before dependent implementation, review specification quality and conflicting contracts.
- Before technical planning, inspect relevant current code and decisions. Identify reusable components and behavior to preserve.
- Trace source requirements to acceptance conditions, work, implementation, and evidence. Check for omitted requirements and unsupported added behavior.
- Run parallel tasks only when dependencies permit. Use separate checkouts and runtime resources when necessary.
- If shared interfaces, data structures, or dependencies change, coordinate with affected tasks. Review their evidence again.
- Implement small batches. Read the actual diff. Run relevant checks. Integrate early.
- Check important assertions against accepted intent. Select validation from affected behavior and risk.
- Keep checks that did not run, blocked checks, and failed checks visible. Passing checks cover only the behavior they examine.
- Identify specification proposals and their reasons. Follow the project's acceptance rules. Do not silently weaken acceptance conditions.

Read [references/workflow.md](references/workflow.md) when planning or implementing a change.
For specification quality and coverage, read [references/spec-review.md](references/spec-review.md).

## Continue a task

A task belongs to the project. Its chat, checkout, harness, and model can change.
For a planned handoff, save the results before the original executor stops writing.
Before transferring responsibility, confirm that the original writers stopped.
The next executor must check current ownership and actual state before taking responsibility.

- Record the goal, specification and code versions, results, evidence, decisions, incomplete work, and next action.
- Use [assets/handoff.md](assets/handoff.md) when the project has no suitable handoff record format.
- Use ordinary Git to transfer commits. For other necessary results, use authorized storage and recovery information.
- If necessary results are missing, continue only work that does not depend on those results.
- If the original executor's stopped state is uncertain, use a separate worktree. Keep its results for review.

## Collaborate when necessary

Link cooperating tasks to the complete business outcome and their accepted shared contract.
Keep component acceptance separate from complete workflow acceptance.
Use existing task assignments, branches, and integration duties. One person can perform several duties.
Do not require collaboration setup for an independent task.
For developer cooperation or multiple active chats, read [references/collaboration.md](references/collaboration.md).

## Use subagents when useful

For delegation, worker results, or outstanding subagents, read [references/subagents.md](references/subagents.md).
Keep short changes and dependent steps with the main agent.
The main agent retains complete requirement acceptance and integration responsibility.
Check actual artifacts and evidence before accepting a worker's result.
Keep partial results, unfinished workers, and pending decisions visible during handoffs.
Check stopped execution before reassigning write scope or removing resources.
Do not require subagents for independent development.

## Accept and publish

Check requirement coverage, actual changes, dependencies, and evidence.
Bind evidence to the exact commit or snapshot, specification version, and relevant environment.
If any of these change, review whether the evidence still applies.
Record the applicability conclusion and its reason. Keep unassessed evidence visibly unassessed.

Required conditions need applicable passing evidence for complete acceptance.
If required validation fails, is blocked, or did not run, report incomplete acceptance and the remaining work.
Before final acceptance, reconcile accepted changes with the authoritative specification and affected records.
Follow the project's specification maintenance model and existing authorization.

Before integration, check the current target.
Validate the actual combined candidate when the target or relevant dependencies changed.

Check development permission, integration permission, and release authorization separately.
Continue routine actions that the user already authorized. This skill does not expand authorization.

Use the existing release entry.
Record the exact candidate commit, artifact hashes, and target environment before publication.
Use only the recorded candidate for this release.
Check combined validation and the release owner.

At execution, verify that the candidate remains selected and eligible.
Reject superseded requests through the release system.
For risky publication, check applicable compatibility, rollout observations, stop conditions, and authorized recovery.

If releases compete, old requests remain, or results are uncertain, check the actual release system before deployment.
Cancellation or timeout does not prove failure or rollback.
Read [references/delivery.md](references/delivery.md). If necessary, use [assets/release.md](assets/release.md).

## Preserve and remove worktrees

Assess commits, task acceptance, releases, worktree removal, and chat archives separately.
If the user authorized automatic cleanup, apply that policy without repeated confirmation when all removal conditions hold.
Stop removal for unknown ownership, active use, or missing preservation of necessary results.
Continue other work when possible.

Prefer native tools that save recoverable archives.
The bundled `snapshot`, `verify`, and `restore` commands do not remove sources or prove that writers stopped.
Keep the worktree protected between preservation checks and removal.
Read [references/recovery.md](references/recovery.md) before recovery or removal.
If you cannot maintain that protection, keep the directory and report the missing control.

## Resources

| Need | Read or run |
| --- | --- |
| Installation or first use | [references/install.md](references/install.md); `scripts/install.py` |
| Internal document writing | [references/writing.md](references/writing.md) |
| Specification quality and coverage | [references/spec-review.md](references/spec-review.md) |
| New features or existing systems | [references/workflow.md](references/workflow.md); [assets/change.md](assets/change.md) |
| Developer cooperation or multiple active chats | [references/collaboration.md](references/collaboration.md) |
| Delegation, worker results, or outstanding subagents | [references/subagents.md](references/subagents.md) |
| Workspace inspection or recovery | `scripts/workspace.py --help`; [references/recovery.md](references/recovery.md) |
| Acceptance, integration, or publication | [references/delivery.md](references/delivery.md) |

At the end, report completed work, validation evidence, unverified scope, and the handoff record location.
Do not substitute filled templates or more documents for task completion.
