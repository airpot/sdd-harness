# Optional Native Hooks

Use these controls only for a project with explicit hook setup authorization.
Ordinary skill installation does not change host configuration.
Hooks add checks at supported tool boundaries. Keep native permissions, release controls, and recovery conditions.

## Prepare a project

Find `scripts/hooks.py` in the installed skill. Use Python 3.10 or a subsequent version.
Keep the accepted task in the existing project record.
Select owned paths and the code, tests, configuration, and specification inputs for check evidence.
Do not select unrelated directories or secrets as evidence inputs.

```text
python <skill>/scripts/hooks.py bind --repo <project> --session <native-session-id> --task tasks/current.md --scope src --scope tests --basis src --basis tests --basis requirements.md --required-check unit
python <skill>/scripts/hooks.py configure --repo <project> --host codex --output <unused-config.json>
python <skill>/scripts/hooks.py configure --repo <project> --host codex --merge <existing-hooks.json>
```

For ZCode, use `--host zcode` and the user configuration file.
ZCode does not execute project-level hooks in its current documented version.
The merge keeps unrelated entries and an exact backup. Repeated identical setup makes no change.
Before setup, make sure that the user authorizes this configuration destination.
Before use, examine generated commands, interpreter paths, and native trust in a fresh session.
For Codex, use its native hook review. Configuration presence does not prove activation.

## Use the four handlers

The operation handler examines common structured write paths and patch headers, including move destinations.
Known scope conflicts prevent a new binding. Unbound sessions cannot use supported writes while another binding is active.
The handler rejects selected direct destructive and publication commands.
Use the project's controlled release or recovery entry instead. Hooks do not supply release authority.
Arbitrary shell code, later input to existing processes, and unsupported host tools have incomplete coverage.

Use this command for a check with retained process evidence:

```text
python <skill>/scripts/hooks.py check --repo <project> --session <native-session-id> --name unit -- python -B -m unittest discover -s tests
```

The evidence handler keeps actual exit results, log files, and input hashes before and after execution.
Each check keeps its command and a separate result record. Later success does not replace initial failure evidence.
Do not put credentials in check arguments. Apply the project's private-data rules to retained commands and output.
After input changes, old evidence cannot satisfy a completed-task claim.
Process success does not prove test quality, requirement coverage, or semantic acceptance.
Select required check names from the accepted task. Do not select a trivial command only to pass the gate.
On timeout, examine descendants and external outcomes before another attempt.

For shared execution control, first obtain a current claim under [coordination rules](coordination.md).
Add `--claim <claim-token> --executor <host:instance:session>` to the binding command.
Use the same native session in the executor identity and `--session`.
Keep binding scope inside the claim scope.
Independent read-only claims can bind overlapping scopes. They do not gain write or write-capable check authority.
Use a fixed snapshot when changes can affect a read-only review.
If a shared registry is active, an unclaimed binding cannot satisfy controlled operations.
Without project coordination, legacy local bindings remain available.
Supported writes, checks, and completion examine the current claim and accepted task revision.
Expired, transferred, closed, or mismatched claims cannot supply current authority.
Hook release removes the local binding only.
After the recovery conditions for the shared claim pass, close that claim.
Registry inspection alone does not enable shared coordination or invalidate ordinary local bindings.
After explicit check recovery, a late callback cannot make the recovered check pass.
Keep its late observations separately. Use a new actual check for new passing evidence.
An interrupted local evidence write must leave a shared run that permits explicit recovery.
Local process evidence alone does not complete finalization. A shared run that is still active blocks task completion.
This order protects new checks. It does not rewrite earlier inconsistent `passed` shared and `running` local records.
For those legacy records, keep the evidence and use a controlled project migration before you reuse their binding.
Apply the [wrapper and writer conditions](coordination.md#return-recover-and-close) before recovery.

The checkpoint handler keeps one current checkpoint per binding and bounded event metadata.
It runs after supported events and gives record references at startup or resume.
It does not copy transcripts, run retrieval, or execute tests automatically.
After context replacement, examine the task record, source state, and evidence applicability directly.

```text
python <skill>/scripts/hooks.py worker --repo <project> --session <native-session-id> --id <worker-id> --value returned
python <skill>/scripts/hooks.py worker --repo <project> --session <native-session-id> --id <worker-id> --value accepted
python <skill>/scripts/hooks.py status --repo <project> --session <native-session-id> --value completed
python <skill>/scripts/hooks.py inspect --repo <project>
```

Use `running` before worker execution. Use `returned` only after actual return evidence.
Before `accepted` or `rejected`, complete the main-agent examination in [subagent rules](subagents.md).
Native worker events record execution state. They do not accept results or prove descendant termination.
For hosts without these events, use explicit worker records. Missing worker identity limits automatic scope control.

The completion handler examines only an explicit `completed` status.
Use `progress`, `partial`, `blocked`, or `paused` when applicable. These statuses permit the current turn to end.
After two unsuccessful hook continuations, the handler records blocked acceptance and permits the turn to end.
This limit does not make the task completed. A final response can still have errors.
The handler does not infer acceptance from the assistant's prose.

## Keep ownership and activation limits

After native inspection proves the relevant writers stopped, use `release --repo <project> --session <native-session-id>`.
This releases only the local binding. It does not remove a worktree or stop a process.
`SessionEnd` and interruption keep checkpoints. They do not release ownership or remove data.
Before archival or removal, use [recovery](recovery.md), including necessary hook state and check logs.

Keep scripts and project state available for later evidence checks.
The checkout-specific hook state directory is `.sdd-harness/hooks/`. Apply the project's private-data and retention rules.
Shared claims use the separate registry from [coordination rules](coordination.md).
An agent with sufficient filesystem access can change local policy. These hooks are not a security boundary.
The handler has no distributed writer registry. Local records do not prove that other writers are absent.

Codex and ZCode have configuration generation. For each host, examine native activation and events on the target machine.
A version-specific native adapter is necessary for DeepSeek Harness. This script does not claim that integration.
Do not register unsupported events or substitute a compatibility bridge without capability checks.
Keep existing RTK and context-mode hooks. Do not assume execution order between independent hook handlers.
If hook execution fails, report degraded control. Independent operation controls are still necessary for important effects.

Provider references: [Codex](https://learn.chatgpt.com/docs/hooks), [ZCode](https://zcode.z.ai/en/docs/hooks),
and [DeepSeek tool execution](https://deepseek-harness.github.io/deepseek-harness/reference/tool-execution-pipeline).
