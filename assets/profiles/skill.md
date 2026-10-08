# Skill Project Prompts

Use these prompts for a reusable agent skill and its portable resources.
For selection and composition, read [project profiles](../../references/project-profiles.md).
Fill relevant prompts in the existing record. Keep its format and authority.

## Specification prompts

- Identify intended users, typical requests, and the desired observable outcome.
- State activation conditions and excluded requests.
- Define accepted inputs, output artifacts, and failure behavior.
- If the skill can cause side effects, state overwrite, external action, and authorization rules.
- Identify required resources, dependencies, supported hosts, and access limits.
- Define how the installed skill finds its own resources.
- If scripts exist, define their inputs, outputs, and consequential side effects.
- Separate format requirements from actual execution outcomes.

Keep resource links inside the portable bundle.
Use existing project tools and accepted installation targets.
Do not require scripts or a new resource structure for an instruction-only skill.

## Acceptance example

Suppose the accepted export contract preserves an existing output file.
The request exports `notes.md` to an existing `report.md`.
The expected result reports the conflict and preserves the existing bytes.
The check examines the response and actual output directory.

A general explanation request without an export request must not activate this example export skill.
The negative case checks both the selected behavior and absence of export effects.
These example rules apply only when the project accepts them.

## Conditional harness checks

- If metadata or resource layout changes, check the required format and local links.
- If activation behavior changes, run positive and negative requests in fresh contexts.
- For behavior acceptance, inspect actual artifacts and side effects against the accepted outcome.
- If scripts change, run their meaningful input and failure cases.
- If dependencies change, check resource access in the supported host.
- If packaging changes, compare source, archive, extracted, and installed inventories and hashes.
- For each applicable payload, retrieve the resources that execution actually needs.
- If installation changes, check repeated installation and protection of locally changed files.
- If model variation affects acceptance, repeat bounded trials under stated conditions.

Static format checks establish structural validity only.
They do not prove activation quality, correct outcomes, or absence of unauthorized effects.
Record exact payloads, model conditions, actual results, and remaining limits in the existing evidence record.
