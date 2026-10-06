# Internal Document Writing Policy

## Scope and precedence

Use English for internal development prose that you create or change while using this skill.
This includes specifications, plans, design decisions, interface descriptions, validation records, handoff records, release records, and recovery instructions.
Apply the policy to changed sections. Do not translate unrelated historical documents.

Follow explicit user language requests and mandatory project formats.
If a project rule requires another language, keep that language and record the exception briefly.
Do not replace an accepted specification merely to change its language.
Keep user conversation in the user's language unless the user requests another language.

Keep source quotations, identifiers, API fields, commands, paths, logs, and tool results unchanged.
Write explanations in the language selected under the precedence rules above.
Do not use this policy to change program behavior, evidence, authorization, or acceptance conditions.

Keep the policy reference in the project's existing development instructions or policy location when creating those records.
If no location exists, use `.sdd-harness/project.md`.
Do not create duplicate policy documents or edit global agent configuration.

## Use ASD-STE100 writing rules

Use ASD-STE100 Issue 9 as the writing reference.
These instructions summarize selected rules. They do not replace the standard or its dictionary.

- Write each procedural sentence with no more than 20 words.
- Keep descriptive sentences within 25 words and paragraphs within six sentences.
- Give one action per procedural sentence. Use direct commands and active voice.
- If a condition controls an action, state that condition before the command.
- Keep a sentence on one topic. Retain words necessary for correct meaning.
- Separate instructions from explanatory notes.
- Use dictionary words with their approved meanings and parts of speech.
- Define necessary software technical nouns and technical verbs. Keep their meanings and grammatical roles fixed.
- Use one technical term for each concept. Avoid idioms and ambiguous abbreviations.
- Divide long noun groups. Define a shorter term for a necessary long technical name.

Use the [official standard](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf) for exact rules and uncertain vocabulary.
The [official overview](https://www.asd-ste100.org/about_STE.html) explains the rules and technical terminology.

Do not assume that a short or familiar word has dictionary approval.
If dictionary access is unavailable, keep the text clear.
Identify the unverified vocabulary review.
Use `STE-guided English` until a complete rule, dictionary, and domain-term review supports an ASD-STE100 compliance claim.
Sentence counts alone do not establish compliance.

Do not include the standard or its dictionary in project artifacts without distribution permission.

## Keep software terms consistent

Use existing project terms when their definitions are clear.
For this skill, use these technical nouns:

| Term | Meaning |
| --- | --- |
| task | Work with a stable identity, goal, and acceptance conditions. |
| chat | A native agent conversation. A chat is not a task. |
| main agent | The agent responsible for the complete task and acceptance of delegated results. |
| subagent | An agent that performs a bounded task for the main agent. |
| disposition | The main agent's decision about a returned result and its necessary next action. |
| attempt | One execution of an assigned task at an identified basis. |
| harness | Software that runs an agent and exposes its tools. |
| worktree | A Git checkout with its own working files. |
| snapshot | Saved versioned results with recovery information. |
| archive | Preserved results kept for later recovery. |
| handoff | The procedure for transferring task responsibility. |
| handoff record | The document with task state, results, evidence, and next actions. |
| candidate | The exact proposed code or artifacts for acceptance or release. |
| evidence | A recorded check for an identified object and environment. |
| release | An authorized publication to an identified target. |
| assertion | A test expression that checks an expected property or result. |
| counterexample | An input or state that demonstrates violation of an expected property. |
| integration target | The branch or version that receives accepted changes. |
| migration | A change between persisted data or configuration versions. |
| rollout | Application of a candidate to a defined target population. |
| workload | The input mix and rate used to check system behavior. |
| contract | The accepted agreement about an interface and its observable behavior. |
| consumer | A component that uses an interface provided by another component. |
| provider | A component that implements an interface for a consumer. |
| mock | A substitute used to check selected behavior without the actual component. |

Use these technical verbs only for their stated actions:

| Verb | Action |
| --- | --- |
| integrate | Combine changes against an identified code baseline. |
| deploy | Apply a candidate to its target runtime environment. |
| restore | Recreate preserved results at a recovery location. |

These are project term definitions, not declarations of dictionary approval.
Keep CLI names and API identifiers exact even when their grammar differs from prose.

## Review meaning and evidence

These checks are project requirements in addition to the STE writing rules:

1. Name the actor when responsibility can be unclear. Do not invent an unknown actor to force active voice.
2. State the condition, action, object, and observable result for important procedures.
3. Distinguish requirements, proposals, observations, and accepted decisions.
4. For evidence, retain the exact object, method, environment, result, and source reference.
5. Keep `not run`, `blocked`, `failed`, and `passed` distinct. Do not replace unknown results with successful results.
6. Check that shorter wording preserves authorization, ordering, conditions, and recovery guarantees.

For example, write:

> If the worktree has active writers, keep the worktree. Continue independent work in a separate worktree.

Do not replace this with "Clean up when safe."
Complete the document review before using the document to accept, publish, transfer responsibility, or remove resources.
