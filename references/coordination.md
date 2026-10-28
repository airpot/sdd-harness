# Optional Local Execution Registry

## Keep task authority

Use the existing task or technical-debt board as task authority.
A visible task status is not an atomic execution claim.
The optional `scripts/coordination.py` helper keeps execution ownership in SQLite with Python standard-library modules.
It is not a second task board. No coordinator service or global hook setup is mandatory.
If the accepted tracker supplies sufficient atomic claims, use its authority instead of duplicate ownership stores.

For linked worktrees, the default authority is Git's common directory plus `sdd-harness-coordination`.
The helper resolves this directory through Git. A `.git` file is not necessarily a directory.
For non-Git projects, the default is `.sdd-harness/coordination`.
The optional project file `.sdd-harness/coordination.json` can select an absolute local directory through its `registry` field.
Keep runtime state outside committed task records. Merged registry copies do not supply mutual exclusion.
Separate clones, machines, and registry directories do not automatically share ownership control.
For shared tasks or resources across those boundaries, use a verified project backend.
An unavailable authority prevents conflicting mutations. Independent read-only work can continue.

## Claim an accepted assignment

Before execution, check readiness, dependencies, accepted task revision, scope, and executor capability.
Use a stable requirement file for each task. Keep execution notes elsewhere.
The expected revision is the file's SHA256 digest.
Use the returned token and generation as current ownership references.
Use a different `host:instance:session` identity for each executor. If applicable, append a worker identity.
A chat, host instance, worker, task, and execution attempt are different identities.

```text
python <skill>/scripts/coordination.py claim --repo <project> --task-id TASK-17 --task tasks/TASK-17.md --expect-revision <sha256> --executor codex:desktop:session-a --scope src --resource database:test
python <skill>/scripts/coordination.py inspect --repo <project>
```

The claim transaction allocates the task and all requested resources, or none.
One task has one responsible execution owner by default.
Different tasks can use the same relative path in separate worktrees when no actual shared resource conflicts.
Branches and worktrees do not isolate ports, databases, containers, or external effects.
Use resource keys that identify actual shared targets.

For delegation, create a distinct child task with `--parent <claim-token>` and a limited scope.
Keep the child scope within the parent scope and exclude active child scopes from parent writes.
Use `--read-only` for an assignment without write authority.
If source changes can affect review, use a fixed snapshot for read-only assignments.
Use `--depends-on <task-id>` for dependencies that require accepted current results.
The helper binds dependency identities, task revisions, and result hashes.
At controlled execution, changed dependency evidence prevents continued use of that assignment.
Child assignments do not give release authority.

## Return, recover, and close

Do not combine task status, execution status, result disposition, and evidence of stopped writers.
Use `finish` with a result file to record return. Return does not accept the result or stop processes.
Only after result examination and actual observations of stopped writers, use `close`.
Preserve results, logs, descendant results, and ownership history before transfer or closure.
Resolve active children and active or uncertain commands first.

For a lease, use a project-selected renewal interval. No universal heartbeat interval is mandatory.
Expiry makes the claim suspect. It does not authorize takeover or prove stopped execution.
Before transfer, examine actual host observations to confirm stopped writers.
If writers remain unknown, use another checkout and controlled result admission.
The `--writers-stopped` flag records an assertion. It cannot observe or terminate writers.
After transfer, reject old tokens at controlled operation and result boundaries.
For arbitrary filesystem writers, isolation or confirmed termination is necessary.

The optional `run` command keeps command evidence and resource ownership.
On timeout or an unknown result, examine descendants and external effects before recovery.
Use `resolve-run` only with actual outcome evidence and stopped-writer confirmation.
This recovery also applies when a terminated wrapper leaves a `running` record.
Hook checks keep a nonpassing recovered attempt before a new check or binding release.
Do not delete locks manually or start a replacement command merely because a window closed.

Keep [hook limits](hooks.md), [subagent rules](subagents.md), and [delivery controls](delivery.md) for their respective boundaries.
Only the actual receiver can enforce current authority for its mutations.
