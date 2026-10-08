# Testing Accepted Behavior

## Select the route

For executable behavior changes, follow the project's testing policy.
When useful under that policy, use the next-test cycle.
This cycle is test-driven development (TDD).
For documentation and low-impact formatting, direct content, link, or rendering checks can suffice.
Do not require a new test framework or every test type.

For ambiguous acceptance, identify the rule, a distinguishing example, and any unresolved question.
Use [specification review](spec-review.md) before work that depends on an unresolved correctness-critical choice.
Derive expected values from accepted rules or suitable independent references.
When the expected result needs explanation, record the reference and its applicability.
Candidate output and model agreement are not independent acceptance references.

## Use the next-test cycle

1. List useful cases for the changed behavior and necessary preservation.
2. Select one case that distinguishes accepted behavior from a plausible failure.
3. Write one meaningful check with an accepted expected result.
4. Run the check before implementation. Keep its input, command, result, and code basis.
5. Classify the result before treating it as red evidence.
6. If the check fails meaningfully, implement a small complete change for that case.
7. Run that check and necessary preservation checks.
8. If useful, refactor the passing implementation. Repeat affected checks after the refactor.
9. Select the next useful case from remaining uncertainty and observed results.

Do not generate all speculative detailed tests before learning from the next case.
Do not replace a complete small change with an incomplete fragment merely to minimize lines.
If a check passes before implementation, determine whether it exercises the proposed change.

| Observed result | Meaning and next action |
| --- | --- |
| Behavior executes and violates the accepted result | Retain the counterexample as behavior red evidence. |
| The intended new interface is absent | Record expected interface absence separately. Implement the accepted interface. Then execute its behavior check. |
| An unrelated import, fixture, runner, or environment fails | Repair or isolate the setup. This result does not establish behavior red evidence. |
| Required behavior cannot be exercised | Keep the limitation visible. Use applicable evidence without claiming an observed behavior failure. |

Example: a retry rule permits three attempts, returns the first success, and retains the final exception after three failures.
List immediate success, later success, and exhausted attempts as useful cases.
Start with an executed failure that demonstrates the wrong attempt limit.
Implement the small retry change. Then check early success and the accepted final exception.
If the retry interface is new, record its initial absence separately from an executed wrong attempt count.

## Characterize without accepting defects

Characterization checks record observed behavior in an existing system.
Label the observation and its code basis. Compare it with accepted intent before deciding to preserve or change it.
If intent is unresolved, keep the observation separate from the acceptance expectation.
If a snapshot records a known defect, do not accept that defect as correct behavior.
Do not accept snapshot updates automatically or copy candidate output into expected results.
If accepted behavior changes, update obsolete checks with the accepted reason and retain useful original defect evidence.

## Check contracts and complete effects

For cooperating interfaces, use [collaboration checks](collaboration.md) on the actual required consumer and provider combination.
An interface contract check examines compatibility for its tested requests, responses, errors, and versions.
Schema validation alone does not establish consumer compatibility or required business effects.
Mocks establish only the behavior they simulate.
When applicable, check required persistence, authorization, emitted effects, and complete workflows.
Keep untested combinations and effects visible before complete acceptance.

## Add checks only when justified

For repeated boundary violations, consider existing architecture tests or static analysis under [domain guidance](domain.md).
Use property checks for accepted invariants across useful inputs.
Use metamorphic checks only with a justified relation between inputs and outputs.
Use differential checks only with a suitable independent reference and known comparison limits.
When important assertions need evidence that they detect relevant faults, use mutation checks.
Retain seeds, counterexamples, setup, and reference versions needed to replay failures.
Passing sampled inputs do not prove behavior for every input.

## Protect test meaning

Review weakened assertions, removed checks, skips, mocks, discovery settings, and runner changes in the actual diff.
Confirm that the intended checks ran. A successful command that discovers zero tests does not establish behavior acceptance.
Accepted requirement changes can justify test changes. Record their basis and preserve necessary checks for remaining requirements.
For material risk, use available controlled acceptance procedures, such as independent review or an existing protected check runner.
Check actual controls before claiming enforcement. Written instructions cannot make hidden checks inaccessible or enforce permissions.
Keep script results, instruction evaluations, and complete workflow evidence distinct.
