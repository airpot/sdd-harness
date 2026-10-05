# Multiple Chats, Machines, and Agents

## Keep project records small

Use the existing task system.
If the project has no record convention, use these locations:

- `.sdd-harness/project.md`: specification entry, shared interfaces, task index, release entry, authorization, cleanup policy, and document policy reference.
- `.sdd-harness/tasks/<task-id>/handoff.md`: task checkpoints and evidence index.
- `.sdd-harness/local/`: observations of local paths, chats, and runtime resources.

Ignore local records according to project rules.
Local records do not establish authority across machines.
Apply [the writing policy](writing.md) to new and changed internal records.
Keep an existing project policy location. Do not create a second policy file.

Before taking responsibility, read shared records and check actual state.
Resolve conflicting records through coordination. Do not assign ownership by the latest timestamp.
If the project has an atomic ownership or controlled start mechanism, use that mechanism.
Otherwise, assign separate tasks and worktrees explicitly.
Do not start simultaneous work on the same task before confirming current ownership.

## Check before writing

Identify the repository, worktree, machine, harness, native chat, and task.
Record the model separately.
A branch name, window title, or identical model does not identify an executor.

Check host chats, tasks, and background execution records for active use.
The bundled `inspect` command observes Git only.
Its `activity: unknown` result does not mean idle.
Isolate shared databases, ports, containers, and logs when necessary.
A worktree isolates files only.

If a new chat enters a busy worktree, read a fixed snapshot or obtain a separate worktree.
Do not commit, clean, or publish from the original worktree without authority.

## Transfer responsibility

For a planned handoff, save results and evidence first.
Stop the original writes before transferring responsibility.
After an unexpected disconnection, use the latest accessible checkpoint.
List any newer results that can be missing.

An expired heartbeat does not prove that execution stopped.
If the original machine is unreachable, continue in a separate worktree.
If the old executor returns, check current ownership before writing.
Keep unaccepted results as proposals.
Task files do not stop old processes.

Across machines, provide the repository reference, exact commit or snapshot, necessary artifacts, checksums, and recovery steps.
Transfer results to a user-authorized location.
Check the results on the receiving machine.
Do not transfer sensitive artifacts or credentials by default.
Treat physical paths and native chat IDs as source references only.

## Use different harnesses

Use the same skill instructions across agents.
Read [installation instructions](install.md) for their locations.
Check each host's actual tools and hooks.
Existing configuration or identical event names do not prove equivalent guarantees.

If automatic loading is unavailable, invoke the skill explicitly.
If necessary, add a short project `AGENTS.md` entry that points to this skill and its internal document policy.
Keep existing content. Obey existing instructions.
Do not change global user configuration to force skill loading.

If exclusive control is unverified, stop writes or releases for the conflicting resource.
Report the missing control. Continue independent work.
Do not create a coordination platform or a distributed lock to use this skill.
