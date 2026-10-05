# Installation and Use

This portable skill uses `sdd-harness/SKILL.md` as its entry.
Extract the release ZIP. Copy the complete directory into the target agent's skills directory.
The scripts need Python 3.10 or later. Workspace commands also need Git 2.29 or later.
Instructions and templates do not need Python.

## Install

Run one command from the extracted package location.
The installer copies files only. It does not change global configuration, connect services, or install dependencies.

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
Install the same version on each machine.
Synchronize project records through the existing repository and authorized artifact storage.

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
Read [the writing policy](writing.md) before creating internal project documents.

## Verification limits

All agents use the same instruction and resource set.
Portability tests cover copying, installation, and workspace scripts.
Discovery paths come from official documentation. Successful copying does not prove each product's complete runtime behavior.

The skill provides workflow and record instructions.
It does not provide distributed locks, forced process termination, or release credential isolation.
Check these guarantees at the project's existing entry when using them.

Official installation sources, checked on 2026-10-05:
[Codex Skills](https://learn.chatgpt.com/docs/build-skills),
[ZCode Skill](https://zcode.z.ai/en/docs/skill),
and [DeepSeek Harness Skills](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md).
