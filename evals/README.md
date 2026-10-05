# Instruction Evaluation

Use these saved scenarios to compare skill revisions.
They test executor decisions and disclosures in isolated simulations.
They do not prove host enforcement, deployment success, or model performance across products.

## Files

- `scenarios.json`: executor requests and raw facts.
- `criteria.json`: evaluator-only criteria.
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
