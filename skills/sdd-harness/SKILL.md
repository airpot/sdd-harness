---
name: sdd-harness
description: Use when specification-driven development spans changes, chats, worktrees, machines, or coding agents. Use when resuming tasks, checking acceptance evidence, preparing releases, or recovering project worktrees.
metadata:
  version: "0.2.0"
---

# SDD Harness

Keep requirements, changes, evidence, and handoffs consistent.
Use the project's existing specifications, Git tools, and host tools.
Do not create a management platform to use this skill.

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
- Run parallel tasks only when dependencies permit. Use separate worktrees and runtime resources.
- If shared interfaces, data structures, or dependencies change, coordinate with affected tasks. Review their evidence again.
- Implement small batches. Read the actual diff. Run relevant checks. Integrate early.
- Keep checks that did not run, blocked checks, and failed checks visible. Passing checks cover only the behavior they examine.
- Identify specification proposals and their reasons. Follow the project's acceptance rules. Do not silently weaken acceptance conditions.

Read [references/workflow.md](references/workflow.md) when planning or implementing a change.

## Continue and coordinate

A task belongs to the project. Its chat, machine, harness, and model can change.
For a planned handoff, save the results before the original executor stops writing.
The next executor must check current ownership and actual state before taking responsibility.

- Record the goal, specification and code versions, results, evidence, decisions, incomplete work, and next action.
- Use [assets/handoff.md](assets/handoff.md) when the project has no suitable handoff record format.
- Across machines, transfer commits or recoverable snapshots, necessary artifacts, and checksums.
- If necessary results are missing, continue only work that does not depend on those results.
- If the original executor's stopped state is uncertain, use a separate worktree. Keep its results for review.

Local records and Git handoff files do not provide distributed locks.
For exclusive task ownership or publication, use verified host, task-system, or CI controls.
Do not create a shared lock protocol by default.
For multiple executors, read [references/collaboration.md](references/collaboration.md).

## Accept and publish

Check requirement coverage, actual changes, dependencies, and evidence.
Bind evidence to the exact commit or snapshot, specification version, and relevant environment.
If any of these change, review whether the evidence still applies.
Check development permission, integration permission, and release authorization separately.
Continue routine actions that the user already authorized. This skill does not expand authorization.

Use the existing release entry.
Record the exact candidate commit, artifact hashes, and target environment before publication.
Use only the recorded candidate for this release.
Check combined validation and the release owner.

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
| New features or existing systems | [references/workflow.md](references/workflow.md); [assets/change.md](assets/change.md) |
| Multiple chats, machines, or agents | [references/collaboration.md](references/collaboration.md) |
| Workspace inspection or recovery | `scripts/workspace.py --help`; [references/recovery.md](references/recovery.md) |
| Acceptance, integration, or publication | [references/delivery.md](references/delivery.md) |

At the end, report completed work, validation evidence, unverified scope, and the handoff record location.
Do not substitute filled templates or more documents for task completion.
