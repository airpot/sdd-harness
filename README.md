# SDD Harness

A portable skill for specification-driven development across chats, worktrees, and coding agents.

Current version: **0.5.1**.

Independent development is the default. Keep small tasks brief in existing project records.
Use collaboration procedures only when work needs cooperation.
Ordinary independent tasks need no frontend/backend split, role profiles, new contract format, mock service, or team CI setup.

The skill combines accepted specifications and incremental changes from OpenSpec with clarification and consistency checks from Spec Kit.
Use the project's existing specifications and tools. Neither framework is a required dependency.

## Use cases

- Continue development from a task handoff.
- Continue independent tasks across chats, checkouts, and harnesses.
- For cooperating developers, connect component tasks to one accepted contract and the complete business outcome.
- Distinguish mock results from actual provider, consumer, and combined workflow evidence.
- Review shared changes and reference existing project commands, runtime resources, and integration duties.
- Check acceptance evidence against exact code and specification versions.
- Review specification quality and trace source requirements to implementation and evidence.
- Review test assertions against accepted intent and retain useful counterexamples and regression evidence.
- Plan changes from relevant current code and existing components.
- Validate the actual combined candidate against the current integration target.
- Check candidate eligibility when a release executes.
- Select system, performance, security, migration, and recovery checks from affected behavior and risk.
- Keep mandatory validation gaps visible in acceptance verdicts.
- Reconcile accepted behavior with the project's authoritative specification.
- Prepare releases through the project's existing publication entry.
- Preserve results before authorized worktree removal.
- Write internal development documents in English with ASD-STE100 writing rules.

## Install for Codex

The repository root is the skill directory. It contains `SKILL.md`, `scripts/`, `references/`, and `assets/`.
Clone it directly into a discovered skills directory.
For example, use PowerShell on Windows:

```powershell
git clone https://github.com/airpot/sdd-harness.git "$HOME/.agents/skills/sdd-harness"
```

Then invoke `$sdd-harness` in Codex.
If unavailable, refresh skill discovery or start a new chat.
If the destination exists, preserve the old installation before replacing it.

Direct cloning also retains repository development records.
For an installation with only the thirteen skill files, use the installer:

```text
git clone https://github.com/airpot/sdd-harness.git
cd sdd-harness
python scripts/install.py --into "~/.agents/skills"
```

For ZCode, use `~/.zcode/skills` as the installation parent.
For DeepSeek Harness, use the project's `.dsh/skills` or its configured user skills directory.
Read [installation instructions](references/install.md) for discovery, updates, and alternative paths.

The installer refuses to overwrite different content.
Before updating, preserve the existing installation outside discovered skills directories.

## Install from the package

Download [sdd-harness-0.5.1.zip](dist/sdd-harness-0.5.1.zip) and its [SHA-256 file](dist/sdd-harness-0.5.1.sha256).
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

Read the [skill entry](SKILL.md) for the workflow and relevant resources.
Project records belong in the target project. Keep them separate from the skill installation.
Use existing project records before adding new files.

## Internal document policy

New or changed internal development prose defaults to English.
Apply the [writing policy](references/writing.md) to specifications, plans, decisions, validation records, and handoff records.
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
python scripts/workspace.py --help
```

Available commands:

| Command | Function |
| --- | --- |
| `inspect` | Read Git observations. It does not establish activity or write permission. |
| `snapshot` | Save HEAD history, current regular files, and selected ignored results outside the worktree. |
| `verify` | Check archive contents and hashes. |
| `restore` | Restore preserved results into a new directory. |

These commands do not delete source worktrees.
For removal conditions and supported recovery scope, read [recovery instructions](references/recovery.md).

Cooperating developers can use ordinary assigned tasks, branches, and independent checkouts in one repository.
The workflow requires no cross-machine execution claims, heartbeat leases, or coordination service.
Written task scopes do not enforce native permissions. Check actual project and host controls before claiming enforcement.
The installer does not configure project CI or release credentials.

## Verify and build

Run the test suite:

```text
python -m unittest discover -s tests -q
```

Build a new package at an unused output path:

```text
python tools/package_skill.py --source . --output dist/sdd-harness-local.zip
```

The builder checks relative references and ZIP integrity. It refuses to overwrite an existing output.
Its output includes the archive SHA-256 hash.
The tests cover workspace preservation and recovery, installation, and packaging.
They do not establish full runtime compatibility across products, machines, or operating systems.

Read the [behavior specification](specs/sdd-harness.md) for the skill's accepted requirements.
Use the [saved instruction evaluations](evals/README.md) to compare executor decisions across revisions.
Evaluation criteria and complete outputs remain separate from executor inputs.
The current instruction suite contains 28 cases and 84 criteria, including independent and optional collaboration workflows.
Isolated host evaluations exercise actual fixture actions in repeated fresh trials.
The repository-only host simulator checks files, hashes, behavior, and attempted actions. It is not included in the skill package.
Read the [0.5.0 workflow validation record](evals/results/0.5.0-validation.md) for results, source-review repairs, and applicability limits.

The [0.5.1 distribution record](evals/results/0.5.1-validation.md) covers the root layout, installer filtering, and package validation.
