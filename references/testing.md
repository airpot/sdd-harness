# Testing Accepted Behavior

## Select the route

For executable behavior changes, obey the project's testing policy.
If the next-test cycle helps the task with this policy, use it.
This cycle is test-driven development (TDD).
For documentation and formatting with small effects, content, link, or rendering checks can be sufficient.
Select the test types necessary for the task.
A new test framework and all test types are not mandatory for each task.

If an acceptance rule can give results that are not compatible, find the accepted rule.
Give an example that shows the difference and each missing decision.
If correctness makes a decision necessary, use [specification review](spec-review.md) before work that uses this decision.

Get expected values from accepted rules or applicable references.
Do not use candidate implementation or output as the source of these rules or values.
When expected results make a report necessary, record their source and the conditions that make this source applicable.
Candidate output and reports from models that agree are not sufficient sources from which you can find acceptance independently of the candidate.

## Use the next-test cycle

For a test cycle that helps the task, do these steps:

1. Make a list of cases that help examine changed behavior and necessary behavior that you must keep.
2. Select one case that shows different results for accepted behavior and possible incorrect behavior.
3. Write one check that gives acceptance evidence, with an accepted expected result.
4. Before implementation, do the check.
   Keep its input, command, result, and code identity.
5. Before you use the result as red evidence, find its result category.
6. If the result shows incorrect behavior, make a small change that makes this case's result agree with accepted behavior.
7. Do this check and necessary checks of behavior that you must keep.
8. If refactoring helps the task, change code structure and keep behavior the same.
   Then, do checks with effects from this structure change again.
9. Use information without sufficient evidence and results from execution to select the next case that helps the task.

Before you examine results from the next case, do not make all possible tests with fully specified cases.
Do not replace a small change that completes its scope with a change that does not complete this scope.
A smaller line count does not make necessary work optional.
If a check gives a satisfactory result before implementation, find if it executes the proposed behavior.

| Result from execution | Information and next step |
| --- | --- |
| Behavior executes but its result does not agree with accepted behavior | Keep the counterexample as behavior red evidence. |
| The new interface in accepted behavior is missing | Record the missing expected interface in a different result type. Make the accepted interface. Then, do its behavior check. |
| An import, fixture, runner, or environment not related to the behavior causes failure | Repair the setup or prevent its conflicts with available controls or different resource instances. This result is not sufficient red evidence for behavior. |
| You cannot execute mandatory behavior | Keep a record of this condition. Use applicable evidence. Do not give a report of a behavior failure without execution. |

Example: a retry rule gives a limit of three attempts.
It gives the first success and keeps the last exception after three failures.
Make a list of cases with success at the first attempt, subsequent success, and attempts that include the limit.
These cases help the task.

Start with a result from execution that shows the incorrect attempt limit.
Make the small retry change.
Then, examine success before the last attempt and the accepted last exception.

If the retry interface is new, keep its missing initial state different from an incorrect attempt count from execution.

## Record behavior without defect acceptance

Characterization checks record behavior from execution of a system that the project uses.
Give the observation label and code identity.

Before a decision to keep or change the behavior, compare it with accepted behavior.
If accepted behavior has no decision, keep the source and acceptance status for the observation.
Keep the source and acceptance status for the expected acceptance result.
If a snapshot records a known defect, do not accept this defect as correct behavior.
Do not accept snapshot updates automatically or use candidate output as expected results.

If accepted behavior changes, use the accepted change to correct checks that do not agree with accepted behavior.
Keep initial defect evidence that continues to be applicable.

## Examine contracts and full effects

For interfaces that operate together, use [checks for the combination](collaboration.md) for the mandatory consumer and provider combination.
An interface contract check examines compatibility for its examined requests, responses, errors, and versions.
Schema validation is not sufficient evidence of consumer compatibility or mandatory business effects.
Mocks give evidence only for behavior that they simulate.
When these checks are applicable, examine mandatory storage changes, approval, effects from execution, and full workflows.
Before full acceptance, keep records of combinations and effects without tests.

## Use accepted sources for more checks

For boundary violations that occur again, examine available architecture tests or static analysis in [domain guidance](domain.md).
Use property checks for accepted invariants for inputs that help the task.
If a relation for inputs and outputs has sufficient evidence, you can use metamorphic checks for this relation.
If a reference operates independently, is applicable, and has known comparison conditions, you can use differential checks with it.
When evidence is necessary that important assertions can find related faults, use mutation checks.
Keep seeds, counterexamples, setup, and reference versions necessary for failure reproduction.

Satisfactory results from an input sample are not sufficient evidence of behavior for each input.

## Keep accepted test behavior

Examine changed assertions that accept more behavior, removed checks, skips, mocks, discovery settings, and runner changes in the change's diff.
Make sure that the specified checks executed.
A command with a satisfactory result and zero tests found is not sufficient evidence of behavior acceptance.
Accepted requirement changes can make test changes necessary.
Record the accepted changes and keep necessary checks for requirements that continue to be applicable.

For important risk, use available acceptance procedures with controls.
Examples are a review that operates independently or a check runner with the project's access controls.
Before you give a report of enforcement, examine the controls.
Written instructions cannot prevent access to checks that they do not show.
They also cannot supply native permission controls.
Keep sources, scopes, and status for each evidence type: script results, instruction evaluations, and full workflow evidence.
