# Skill Project Prompts

Use these prompts for an agent skill that you can use again and its portable resources.
For selection and composition, read [project profiles](../../references/project-profiles.md).
Write information for the related prompts in the record that the project uses.
Keep its format and authority.

## Specification prompts

For the related prompts, use these instructions:

- Identify the users that the skill is for.
- Give typical requests and the observable outcome that the project wants.
- Give activation conditions and requests that must not activate the skill.
- Give accepted inputs, output artifacts, and failure behavior.
- If the skill can cause side effects, give overwrite, external action, and authorization rules.
- Identify necessary resources, dependencies, supported hosts, and access limits.
- Give the method that the installed skill uses to find its resources.
- If the skill has scripts, give their inputs, outputs, and side effects that can be important.
- Keep format requirements in a different group from execution outcomes.

Keep resource links in the portable bundle.
Use the tools that the project has and the accepted installation targets.
For a skill with instructions only, do not make scripts or a new resource structure necessary.

## Acceptance example

For this example, the accepted export contract keeps the file that is in the output directory.
The request exports `notes.md` to `report.md`, which is in the output directory.
The expected result gives a conflict report and keeps the file bytes without changes.
The check examines the response and the output directory.

A general explanation request without an export request must not activate this example export skill.
The negative case examines the selected behavior and makes sure that there are no export effects.
These example rules are applicable only if the project accepts them.

## Conditional harness checks

For applicable checks, use these instructions:

- If metadata or resource layout changes, do checks of the necessary format and local links.
- If activation behavior changes, do positive and negative requests in new contexts.
- For behavior acceptance, compare artifacts and side effects from execution with the accepted outcome.
- If scripts change, do their input and failure cases that help show their behavior.
- If dependencies change, do a check of resource access in the supported host.
- If packaging changes, compare source, archive, extracted, and installed inventories and hashes.
- For each applicable payload, get the resources that are necessary for execution.
- If installation changes, do installation. Then, do it again.
  Also do a check of protection for files with local changes.
- If model variation has an effect for acceptance, do trials again with specified limits and conditions.

Static format checks show only that the structure is correct.
They do not show activation quality or correct outcomes.
They also do not show that execution has no effects without authorization.

Record payload identities and their content basis in the evidence record that the project uses.
Also record model conditions, execution results, and remaining limits.
