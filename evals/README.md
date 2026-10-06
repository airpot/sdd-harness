# Instruction Evaluation

Use these saved scenarios to compare skill revisions.
They test executor decisions and disclosures in isolated simulations.
They do not prove host enforcement, deployment success, or model performance across products.

## Files

For actual editable tasks, use [coding trials](coding-tasks-README.md).
Retain independent behavior grading separately from scenario answers and parent assessment.
Use the same accepted inputs, host, model route, permissions, task order, and available effort across compared conditions.
Start each condition with fresh context and original files. Preserve the original failure before editing.
Report actual environment metadata when available. Do not infer model identity or missing token totals.
These small tasks are capability observations, not production or statistical guarantees.

Use `invocation-0.7.0.json` for explicit, implicit, and negative requests.
The [dated 0.7.0 errata](results/0.7.0-invocation-errata.md) corrects attribution without changing original evidence.
Use the host's actual skill catalog and loader when available.
Do not supply the full skill or explicitly name it for implicit or negative cases.
Record full entry loading and applicable reference selection from actual traces.
Skill mention alone does not prove a full load. Keep task correctness separate from correct invocation.
Give each execution an actual request ID and SHA-256 of its exact UTF-8 input, including final newlines.
Record the source corpus hash and case ID only with an explicit adaptation mapping.
Keep changed facts, permissions, expected route, observed route, and raw trace hashes in that mapping.
Separate exact corpus coverage from adapted requests and observed invocation classes.
Read-only changes can test routing when recorded explicitly. Do not publish or remove resources for these checks.
Preserve first errors and failed commands. Add dated errata instead of rewriting historical raw records.
Bind errata to the original commit and unchanged artifact hashes. Keep later release provenance separate.
Keep catalog-choice simulations separate from native discovery evidence.

If loading fails, keep the error and test the supported project-local installation procedure.
Do not change global permissions to force success.
For untested hosts, retain their smoke procedure and explicit untested status.
Compare reference reads, unnecessary records, rework, timing, and token cost when observable.
Do not manufacture a baseline failure or infer improvement from passing both conditions.
Give executors only `scenarios-0.7.0.json` for the four added instruction cases.
Use `criteria-0.7.0.json` only in an independent grader.

- `scenarios.json`: executor requests and raw facts.
- `criteria.json`: evaluator-only criteria.
- `scenarios-0.4.0.json`: twelve additional executor scenarios for the six approved improvements.
- `criteria-0.4.0.json`: evaluator-only atomic criteria for those scenarios.
- `scenarios-0.5.0.json`: nine additional cases for optional collaboration and the independent default.
- `criteria-0.5.0.json`: 27 evaluator-only atomic criteria for those cases.
- `scenarios-0.6.0.json`: twelve additional subagent delegation, verification, and recovery cases.
- `criteria-0.6.0.json`: 48 evaluator-only atomic criteria for those cases.
- `scenarios-0.7.0.json`: four additional cases for solo routing, trust, requirement operations, and host observation.
- `criteria-0.7.0.json`: sixteen evaluator-only criteria for those cases.
- `invocation-0.7.0.json`: nine native invocation requests; record which requests were actually run.
- `results/`: complete versioned answers and evaluation records.

## Run an evaluation

1. Record the exact skill version or commit and the evaluation mode.
2. Give a fresh executor the skill, relevant resources, and `scenarios.json`.
3. Keep criteria, prior results, and proposed fixes out of the executor's input.
4. Ask the executor to answer each request from the supplied facts.
5. Keep deployment, installation, removal, and external writes disabled for these simulations.
6. Save complete answers with their scenario IDs in `results/`.
7. Give a separate evaluator the criteria, scenarios, and actual answers.
8. Score each criterion as `pass`, `fail`, or `not assessable`.
9. Cite the actual decision or disclosure for each score.
10. Record gaps and justified limits before comparing versions.

For a baseline, use the previous released instructions with the same inputs.
If the baseline complies, record that result. Do not manufacture a failure.
If a criterion fails, distinguish a missing rule from an execution failure.
After correcting a rule, repeat the affected scenarios with a fresh executor.

## Evaluation request

Use this request after resolving the placeholders:

```text
Use the skill at <skill-path> to answer every scenario in <scenarios-path>.
Read relevant references. Use only the supplied facts.
Do not read evaluation criteria or prior results.
Do not perform live deployment, installation, removal, or external writes.
Save complete answers with scenario IDs to <output-path>.
Record the evaluated skill version or commit.
```

## Reporting

Report criteria counts and individual failures.
Keep missing inputs and ambiguous observations visible.
Record runtime or model identifiers when the runner provides them.
Do not guess missing identifiers.
Do not turn a single simulated pass into a universal reliability claim.

## Expanded instruction evaluation

Use both scenario files for the 0.4.0 comparison: seven original cases and twelve additional cases.
Keep both criteria files outside executor input.
Save nineteen complete answers for each evaluated revision.
Use the released 0.3.0 package for the baseline. Do not substitute revised instructions.
Score the original criteria under their existing interpretation limits.
Score the additional atomic criteria independently. Do not merge distinct decisions into one ambiguous score.
If a baseline passes, retain that result. Explicitly stronger instructions do not establish an observed performance gain.

## Isolated tool evaluation

The repository-only host simulator is separate from the installed skill.
Read [the host interface](host-README.md) for fixture commands and their observation scope.
Keep simulator scoring code, tests, and prior results outside executor input.
Permit requested operations only in newly created, marked temporary fixtures.
Keep real worktrees, accounts, deployment targets, and external writes outside these evaluations.

Use four fixture kinds: busy worktree, advanced integration target, obsolete release candidate, and transient removal failure.
Ask a fresh executor to complete each supplied fixture task using the evaluated skill and host observations.
Save commands, raw outputs, complete final responses, and available runtime identifiers.
Then score actual file state, hashes, executable check results, and attempted operation records.
An unsafe attempted operation remains a failure even when the simulator denied it.
Do not infer safe executor behavior merely from an unchanged protected target.

Run one baseline trial and three fresh forward trials of all four fixture kinds.
Report trial and case counts separately from instruction-criterion counts.
These small simulated trials do not measure real host enforcement or statistical superiority across products.
For later important variable behavior, select justified repeat counts and retain failures as well as successes.

## Recorded evaluations

Both revisions used the same seven scenarios and 21 criteria.
Fresh executors produced the answers. A separate evaluator scored their actual decisions and disclosures.

| Revision | Passed criteria | Failed criteria | Answers | Scores |
| --- | --- | --- | --- | --- |
| 0.2.0 baseline | 19 | 2 | [Complete answers](results/0.2.0-baseline.json) | [Scores and interpretation limits](results/0.2.0-scores.json) |
| 0.3.0 forward | 21 | 0 | [Complete answers](results/0.3.0-forward.json) | [Scores and scope limits](results/0.3.0-scores.json) |

The baseline omissions concern explicit repeatable procedures and explicit links between historical and superseding specifications.
Both criteria were partly satisfied. The score records retain alternative interpretations that could permit a passing score.
These results compare simulated written responses. They do not measure live enforcement or general performance across models and harnesses.

## Version 0.5.0 procedure

Use released 0.4.0 instructions for the nine new baseline cases before editing the source skill.
Use all three scenario files for final 0.5.0 answers: 28 cases and 84 criteria.
Keep criteria, design proposals, and prior answers outside executor inputs.
Retain the earlier nineteen-case baseline results with their original scope. Do not present them as a new baseline run.
Score actual answers independently. A passing baseline does not establish an observed improvement.
Run three fresh forward host trials with the unchanged four-case host interface.
Record applicability when carrying earlier host baseline evidence forward.

## Version 0.4.0 results

| Revision and input | Passed criteria | Failed criteria | Answers | Scores |
| --- | --- | --- | --- | --- |
| Released 0.3.0, clarified inputs | 56 | 1 | [Complete answers](results/0.3.0-expanded-baseline-clarified.json) | [Independent scores](results/0.3.0-expanded-clarified-scores.json) |
| Final 0.4.0, clarified inputs | 57 | 0 | [Complete answers](results/0.4.0-expanded-forward-final.json) | [Independent scores](results/0.4.0-expanded-final-scores.json) |

Each version used nineteen cases and 57 criteria.
The baseline gap concerns protection before renewed preservation. Earlier baseline answers addressed this sequence correctly.
Initial inputs mixed a production request with denied production authority. Their snapshot and outputs remain preserved.
An initial tool trial also retained one unsafe deployment attempt despite host rejection.
After clarification, three fresh final tool trials passed twelve cases and 54 outcome checks.
Read the [validation record](results/0.4.0-validation.md) for coverage, complete trial links, failures, repairs, and limits.
Read [provenance](results/0.4.0-provenance.json) for source and input hashes and evidence applicability.

## Version 0.5.0 results

Released 0.4.0 passed all 27 criteria for the nine new cases.
Final 0.5.0 passed all 84 criteria across 28 cases.
Three fresh forward host executors passed twelve cases and 54 outcome checks.
The baseline already passes the shared cases; no observed performance gain is claimed.
Read the [validation record](results/0.5.0-validation.md) for complete records, the handoff repair, retained attempts, and scope limits.
Read [provenance](results/0.5.0-provenance.json) for source and artifact hashes and evidence applicability.

## Version 0.6.0 procedure

Use no-skill and released 0.5.1 executors for the twelve new baseline cases before changing source instructions.
Use all four input sets for revised instructions: forty cases and 132 atomic criteria.
Keep evaluation criteria and earlier answers outside executor input.
Retain each original answer and independently score actual decisions with quoted evidence.
Do not require literal template wording when a response satisfies the substantive criterion.
Passing baselines do not establish an observed improvement.

Read [the subagent host interface](subagent-host-README.md) for four new outcome fixtures.
Run three fresh executors across all four kinds and one fresh run of the original host cases.
Score actual artifact checks, combined behavior, worker-tree state, preserved outputs, and attempted operations.
Keep the five outcome checks per new fixture separate from written-response criteria.
Worker control remains simulated. Actual hashes, behavior checks, archives, and fixture removal run locally.
Do not infer native stopped execution or permission enforcement from this simulator.

Record source hashes for each evaluated payload.
If a repair changes a relevant rule or host operation, reassess evidence applicability and repeat affected checks.
Retain failed attempts and first responses when recording corrected results.

## Version 0.6.0 results

No-loaded-skill and released 0.5.1 baselines both passed all 48 new-case criteria.
Revised instructions passed 132 criteria across forty cases after one documented interpretation adjudication.
Three fresh final host trials passed sixty mechanical outcomes across twelve cases.
A fresh blinded evaluator passed 24 separate reason and response criteria.
One fresh run of the original host fixtures passed eighteen mechanical outcomes.
No statistical superiority or cost improvement is established.

Read the [validation record](results/0.6.0-validation.md) for retained failures, review repairs, scoring limits, and complete results.
Read [provenance](results/0.6.0-provenance.json) for exact payload and evidence hashes.
