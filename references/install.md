# Installation and Use

This portable skill uses `sdd-harness/SKILL.md` as its entry.
The Git repository root contains `SKILL.md` and its resources.
For installation from the repository, clone the repository into the target agent's `sdd-harness` skills directory.

Extract the release ZIP.
Make a copy of the full directory in the skills directory for the target agent.
Python 3.10 or a subsequent version is necessary for the scripts.
Git 2.29 or a subsequent version is also necessary for workspace commands.
Python is not necessary for instructions and templates.

Before directory traversal, the installer rejects symbolic links and Windows reparse points.
This includes target inventories that are there before installation.
This check uses `lstat` file attributes.
It does not use `Path.is_junction` from Python 3.12.

## Install

Use one command from the extracted package location.
The installer makes copies of only `SKILL.md`, scripts, references, assets, and optional agent metadata.
It does not include repository documentation, tests, evaluation records, Git metadata, and distributions.
Installation and ZIP building do not include `__pycache__` directories and `.pyc` files in each portable inventory.
These operations use relative paths from each inventory root.
An ancestor with the name `__pycache__` that is not in the source or target skill does not remove skill files from the portable inventory.

Before the scripts make the destination, the two scripts reject an empty portable inventory.
The installer does not change global configuration, connect services, or install dependencies.

```text
# Codex user installation
python sdd-harness/scripts/install.py --into "~/.agents/skills"

# ZCode user installation
python sdd-harness/scripts/install.py --into "~/.zcode/skills"

# Project installation for DeepSeek Harness: use the target project root
python /path/to/sdd-harness/scripts/install.py --into "./.dsh/skills"
```

For Windows, if the `python` command is not available, use `py -3`.
`--into` gives the parent skills directory.
The installer makes the `sdd-harness` directory in this directory.
If the package that is there has the same content, no changes are necessary.
The installer does not replace different content or local changes.

Before an update, move the previous directory to a backup from which you can get the previous results.
Do not keep this backup in a skills directory that the host finds.
Then, install the new version.

For user installation with DeepSeek Harness, use its `<dshHome>/skills` directory from configuration.
For project installation, `.agents/skills` is also available.
Do not select a custom Harness home without its path from configuration.
Enable the skill provider for the profile that you use.

Without Python, make a copy of the full directory.
Do not make a copy of only `SKILL.md`.
Changes in one skill directory copy do not change other copies automatically.
For developers who operate together, use the same instruction version.
Move project records with Git and permitted artifact storage.

## Find and invoke

For discovery and invocation, use the instructions for your host:

- Codex: after installation in a skills directory that the host finds, invoke `$sdd-harness`.
  If invocation is not available, examine sources and disabled settings.
  Refresh the session, or stop it.
  If you stop the session, start the same session again.
- ZCode: refresh Settings > Skills.
  Examine the source and enabled state.
  If skill selection is necessary for the task, select the name `sdd-harness`.
- DeepSeek Harness: examine the skill provider and directories for the profile that you use.
  Use the name `sdd-harness` for invocation.

For the first task, give this instruction:

> Use sdd-harness for this project.
> Examine specifications, tasks, and worktrees before you complete the task.
> Keep necessary handoff records.

To continue, give this instruction:

> Use sdd-harness to continue from the task handoff record.
> Before the next step, examine results, ownership, and evidence.

Automatic selection uses host discovery and model decisions.
Installation is not sufficient evidence that the host makes the skill active in each new chat.
If a specified project entry is necessary, add a short instruction to its `AGENTS.md`.
Keep the instructions that are there.
For example:

> Use sdd-harness for specification-driven development and task handoffs.
> For new or changed development documents for the project, obey its writing policy.

The skill does not install hooks automatically.
As the default procedure, do development work independently.
Setup for tasks that you do together is optional.
For necessary project references and permission checks, read [instructions for tasks done together](collaboration.md).
Before you make development documents for the project, read [the writing policy](writing.md).

## Examine host capabilities

Before you first use the skill, examine the capabilities necessary for the task.
After host, profile, permission, or skill-source changes, do related checks again.
Use a short environment or task record that the project uses.
Do not make a capability service.

To examine host capabilities, do these steps:

1. Make sure that the host shows the skill name and entry path that it uses.
2. Read the full entry with native invocation that is available or a permitted direct read.
3. Read one reference that is necessary for the task.
   Make sure that you can read its contents.
4. If scripts are necessary, use `scripts/workspace.py --help` from the skill directory that the host finds.
5. If a subagent task is necessary, examine one result from a task with its specified scope and conditions.
   For this result, examine the main agent's decision.
6. Before resource changes with important effects, examine the native state and necessary control at this time.

For each related capability, record `verified`, `unavailable`, or `untested` with its version and observation.
A catalog entry is not sufficient evidence of resource access.
Files from a copy are not sufficient evidence of invocation, native interruption, permissions from native controls, or release control.
Do not do deployment or removal only to examine a control's rejection behavior.

If the sandbox cannot read a user skill directory, use a permitted project-local copy of the same portable payload.
Use a discovery location that the host makes available in the permitted workspace.
Examine the version and contents of the copy.
Refresh discovery and do the necessary read again.
Do not disable permissions or change global configuration to get a satisfactory check result.
If invocation continues to be not available, give a report of this condition.

If work can continue independently with available capabilities, continue this work.

For DeepSeek Harness, examine filesystem discovery and the model-facing skill loader in the profile that you use.
There can be a registry and provider without a catalog that you can see or a loader tool.
For each worker, examine its skill and resource access directly.
Parent access is not sufficient evidence of worker inheritance.

A report of native cancellation is not sufficient evidence that descendants stopped.
If you cannot examine or control execution, prevent changes in the scope of its possible effects.
Continue other work with available controls or different resource instances that prevent conflicts with this execution.
At each operation boundary, examine writer state and candidate eligibility at this time.
A previous smoke check with a satisfactory result does not remove these checks from the necessary scope.

## Verification limits

All agents use the same instruction and resource set.
Portability tests include copies, installation, and workspace scripts.
Documentation from the product providers gives discovery paths.
Copies with all necessary content are not sufficient evidence of the full runtime behavior for each product.

The skill gives workflow and record instructions.
Installation does not configure project CI, native permissions, or release credentials.
Before you give a report of enforcement, examine the project and host controls in use directly.

Date of source review: 2026-10-05.
These installation sources are from the product providers:
[Codex Skills](https://learn.chatgpt.com/docs/build-skills),
[ZCode Skill](https://zcode.z.ai/en/docs/skill),
and [DeepSeek Harness Skills](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md).
