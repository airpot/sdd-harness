# SDD Harness

A portable skill for specification-driven development across chats, worktrees, machines, and coding agents.

Current version: **0.3.0**.

The skill combines accepted specifications and incremental changes from OpenSpec with clarification and consistency checks from Spec Kit.
Use the project's existing specifications and tools. Neither framework is a required dependency.

## Use cases

- Continue development from a task handoff.
- Coordinate separate tasks across chats, worktrees, machines, and harnesses.
- Check acceptance evidence against exact code and specification versions.
- Review specification quality and trace source requirements to implementation and evidence.
- Keep mandatory validation gaps visible in acceptance verdicts.
- Reconcile accepted behavior with the project's authoritative specification.
- Prepare releases through the project's existing publication entry.
- Preserve results before authorized worktree removal.
- Write internal development documents in English with ASD-STE100 writing rules.

## Install for Codex

Clone the repository:

```text
git clone https://github.com/airpot/sdd-harness.git
cd sdd-harness
```

Install the complete skill:

```text
python skills/sdd-harness/scripts/install.py --into "~/.agents/skills"
```

Then invoke `$sdd-harness` in Codex.
If the skill is unavailable, refresh or restart the session.

For ZCode, use `~/.zcode/skills` as the installation parent.
For DeepSeek Harness, use the project's `.dsh/skills` or its configured user skills directory.
Read [installation instructions](skills/sdd-harness/references/install.md) for discovery, updates, and alternative paths.

The installer refuses to overwrite different content.
Before updating, preserve the existing installation outside discovered skills directories.

## Install from the package

Download [sdd-harness-0.3.0.zip](dist/sdd-harness-0.3.0.zip) and its [SHA-256 file](dist/sdd-harness-0.3.0.sha256).
Extract the ZIP into a local directory.
From that directory, run:

```text
python sdd-harness/scripts/install.py --into "~/.agents/skills"
```

Without Python, copy the complete `sdd-harness` directory into the target skills directory.
Do not copy only `SKILL.md`.

## Continue a project

Give the agent this instruction:

> Use sdd-harness to continue from the task handoff. Check results, ownership, and evidence before the next action.

Read the [skill entry](skills/sdd-harness/SKILL.md) for the workflow and relevant resources.
Project records belong in the target project. Keep them separate from the skill installation.
Use existing project records before adding new files.

## Internal document policy

New or changed internal development prose defaults to English.
Apply the [writing policy](skills/sdd-harness/references/writing.md) to specifications, plans, decisions, validation records, and handoff records.
The policy uses short instructions, active voice, explicit conditions, and consistent software terms.
Explicit user language requests and mandatory project formats take precedence.
Keep code identifiers, commands, paths, quotations, and raw evidence unchanged.
Use the user's language for conversation unless the user requests another language.

The package uses **STE-guided English**.
No complete ASD-STE100 dictionary or full-standard compliance audit has been performed.

## Workspace tools

The scripts need Python 3.10 or later.
Workspace commands also need Git 2.29 or later.
There are no third-party Python dependencies.

```text
python skills/sdd-harness/scripts/workspace.py --help
```

Available commands:

| Command | Function |
| --- | --- |
| `inspect` | Read Git observations. It does not establish activity or write permission. |
| `snapshot` | Save HEAD history, current regular files, and selected ignored results outside the worktree. |
| `verify` | Check archive contents and hashes. |
| `restore` | Restore preserved results into a new directory. |

These commands do not delete source worktrees.
For removal conditions and supported recovery scope, read [recovery instructions](skills/sdd-harness/references/recovery.md).

The skill does not provide distributed locks, forced process termination, or release credential isolation.
Use verified host, task-system, or CI controls for those guarantees.

## Verify and build

Run the test suite:

```text
python -m unittest discover -s tests -q
```

Build a new package at an unused output path:

```text
python tools/package_skill.py --source skills/sdd-harness --output dist/sdd-harness-local.zip
```

The builder checks relative references and ZIP integrity. It refuses to overwrite an existing output.
Its output includes the archive SHA-256 hash.
The tests cover workspace preservation and recovery, installation, and packaging.
They do not establish full runtime compatibility across products, machines, or operating systems.

Read the [behavior specification](specs/sdd-harness.md) for the skill's accepted requirements.
Use the [saved instruction evaluations](evals/README.md) to compare executor decisions across revisions.
Evaluation criteria and complete outputs remain separate from executor inputs.
