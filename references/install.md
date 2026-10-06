# Installation and Use

This portable skill uses `sdd-harness/SKILL.md` as its entry.
The Git repository root contains `SKILL.md` and its resources.
For direct installation, clone the repository into the target agent's `sdd-harness` skills directory.

Extract the release ZIP. Copy the complete directory into the target agent's skills directory.
The scripts need Python 3.10 or later. Workspace commands also need Git 2.29 or later.
Instructions and templates do not need Python.
The installer rejects symbolic links and Windows reparse points before directory traversal, including existing target inventories.
This check uses `lstat` file attributes and does not depend on Python 3.12's `Path.is_junction`.

## Install

Run one command from the extracted package location.
The installer copies `SKILL.md`, scripts, references, assets, and optional agent metadata only.
It excludes repository documentation, tests, evaluation records, Git metadata, and distributions.
Installation and ZIP building exclude internal `__pycache__` directories and `.pyc` files using paths relative to each inventory root.
An ancestor named `__pycache__` outside the source or target skill does not exclude skill files.
Both scripts reject an empty portable inventory before creating the destination.
It does not change global configuration, connect services, or install dependencies.

```text
# Codex user installation
python sdd-harness/scripts/install.py --into "~/.agents/skills"

# ZCode user installation
python sdd-harness/scripts/install.py --into "~/.zcode/skills"

# DeepSeek Harness project installation: run at the target project root
python /path/to/sdd-harness/scripts/install.py --into "./.dsh/skills"
```

On Windows, use `py -3` if necessary.
`--into` specifies the parent skills directory. The installer creates `sdd-harness` below that directory.
An identical existing package needs no changes.
The installer refuses to overwrite different content or local modifications.

Before updating, move the old directory to a recoverable backup outside the discovered skills directories.
Then install the new version.

For a DeepSeek Harness user installation, use its configured `<dshHome>/skills` directory.
For project installation, `.agents/skills` is also available.
Do not guess a custom Harness home.
Enable the skill provider for the actual profile.

Without Python, copy the complete directory manually. Do not copy only `SKILL.md`.
Copied installations do not synchronize automatically.
For cooperating developers, use the same instruction version.
Transfer project records through ordinary Git and authorized artifact storage.

## Discover and invoke

- Codex: invoke `$sdd-harness` after installation in a discovered skills directory.
  If unavailable, check sources and disabled settings. Refresh or restart the session.
- ZCode: refresh Settings > Skills. Check the source and enabled state. Select `sdd-harness` explicitly if necessary.
- DeepSeek Harness: check the actual profile's skill provider and directories. Load `sdd-harness` explicitly.

For first use, give this instruction:

> Use sdd-harness for this project. Check specifications, tasks, and worktrees before completing the goal. Keep necessary handoff records.

For continuation, give this instruction:

> Use sdd-harness to continue from the task handoff record. Check results, ownership, and evidence before the next action.

Automatic selection depends on host discovery and model decisions.
Installation does not guarantee activation in every new chat.
If the project needs a fixed entry, add a short instruction to its `AGENTS.md` without replacing existing instructions.
For example:

> Use sdd-harness for specification-driven development and task handoffs. Apply its writing policy to new or changed internal development documents.

The skill does not install hooks automatically.
Independent development is the default. Collaboration setup is optional.
For necessary project references and actual permission checks, read [collaboration instructions](collaboration.md).
Read [the writing policy](writing.md) before creating internal project documents.

## Observe actual host capabilities

Before first use, check the capabilities necessary for the current task.
Repeat relevant checks after host, profile, permission, or skill-source changes.
Reuse a short existing environment or task record. Do not create a capability service.

1. Check that the host presents the skill name and actual entry path.
2. Load the full entry through the supported native invocation or an authorized direct read.
3. Read one reference required for the task. Check access to its actual contents.
4. If scripts are needed, run `scripts/workspace.py --help` from the resolved skill directory.
5. If delegation is needed, observe one bounded result and the main agent's disposition.
6. Before sensitive resource changes, check the current native state and necessary control.

For each relevant capability, record `verified`, `unavailable`, or `untested` with its version and observation.
Catalog visibility alone does not establish resource access.
Copied files alone do not establish invocation, native interruption, enforced permissions, or release control.
Do not run deployment or removal merely to test whether a control rejects it.

If the sandbox cannot read a user-level installation, use an authorized project-local copy of the same portable payload.
Use a discovery location supported by the actual host and permitted workspace.
Check the copied version and contents. Refresh discovery and repeat the necessary read.
Do not disable permissions or change global configuration to make the check pass.
If loading remains unavailable, report that limitation. Continue supported independent work when possible.

For DeepSeek Harness, check both filesystem discovery and the model-facing skill loader in the actual profile.
The registry and provider can exist without a visible catalog or loader tool.
For any worker, check its actual skill and resource access rather than assuming parent inheritance.

Native cancellation acknowledgement does not establish stopped descendants.
If execution cannot be observed or controlled, protect the affected scope and continue in supported isolation.
Check current writer state and candidate eligibility at their operation boundaries, even after a successful earlier smoke check.

## Verification limits

All agents use the same instruction and resource set.
Portability tests cover copying, installation, and workspace scripts.
Discovery paths come from official documentation. Successful copying does not prove each product's complete runtime behavior.

The skill provides workflow and record instructions.
Installation does not configure project CI, native permissions, or release credentials.
Check actual project and host controls before claiming enforcement.

Official installation sources, checked on 2026-10-05:
[Codex Skills](https://learn.chatgpt.com/docs/build-skills),
[ZCode Skill](https://zcode.z.ai/en/docs/skill),
and [DeepSeek Harness Skills](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md).
