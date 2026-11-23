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

## Assign checks to stages

| Stage | Main checks |
| --- | --- |
| Development | Unit, component, property, and applicable regression checks. |
| PR and integration | Current combination, interfaces, contracts, and affected source checks. |
| RC acceptance | System and end-to-end checks of the actual deployed candidate. |
| Production rollout | Authorized smoke checks, health signals, and rollout observations. |

Complete applicable unit and component checks before RC acceptance.
Use current evidence for the integrated combination, not only separate branch passes.
An unchanged completed job can supply applicable evidence. It is not necessary for RC to repeat every unit job.
For system checks, use the actual supported UI, API, CLI, MCP, or data entry.
Observe required persistence and other business effects.
A successful click or HTTP response alone is not sufficient evidence of the business result.
Do not use mock checks as evidence for the actual combination.

For changed behavior, select applicable positive, negative, boundary, state, and concurrency cases.
For rejection cases, check both the rejection and absence of forbidden side effects.
Use authorized actors for positive access checks and unauthorized actors for applicable negative checks.

## Maintain useful regressions

When test infrastructure changes process environments, check both implicit inheritance and explicit child environments. Confirm that intended missing, empty, and nonempty inputs reach the actual child. Restored start/end snapshots do not prove intermediate input semantics.
For concurrent regressions, use explicit readiness and release barriers to control the required order. A fixed sleep is not an ordering guarantee. Reap fixture subprocesses before deleting their temporary state, including on assertion failure.

For each bug repair, keep the original reproducer, input, incorrect result, and accepted expected result.
Add a reliable regression at the lowest effective test layer.
If a system boundary caused the defect, add or extend the applicable system test.
When prior execution is available and safe, observe defect failure and repair success.
Do not combine missing-interface results, setup failures, and behavior failures.
Keep important generated counterexamples as durable inputs. A local cache alone is not sufficient.

Agents can propose tests from accepted specifications, diffs, defect reports, and previous failures.
Get expected results from accepted specifications or an applicable independent oracle.
Before mandatory admission, review requirement references, assertions, discovery, side effects, and stability.
For important risk, use independent review or controlled project checks.
When feasible, show that assertions detect the original defect or a representative fault.
Do not accept snapshot updates, weaker assertions, skips, or candidate output automatically.

Maintain usefulness rather than an increasing end-to-end test count.
Use review to remove duplicate or obsolete active cases. Keep historical evidence.
Unless accepted changes or justified replacements remove their applicability, keep bug regressions.
Track defect detection, escaped defects, runtime, and instability when these observations help maintenance.

## Freeze the full gate

For long-lived acceptance services, keep child self-verification and parent exit observations separate. A missing child after-record does not identify a normal exit, exception, or forced termination. Record an execution or final-verification error when the process can still write. If the process cannot run its finalizer, retain the independently observed process identity and exit status; do not synthesize a successful child self-check. Attribute a forced exit only to a matching observed termination action or signal.

Keep missing final self-verification incomplete for publication acceptance. An observed business result or a nonzero child exit without final receipts cannot satisfy a mandatory integrity check. Preserve supported business results separately. A known final-verification error remains failed; receipt loss does not establish a successful check or authorize retry.

Use distinct immutable receipt locations for cleanup attempts. After a termination or receipt-publication error, independently attempt the final observation on the proved process handle. Retain ordered errors and an explicit unconfirmed cleanup disposition before releasing responsibility. Do not mark cleanup complete while the actual child remains live or its exit is unobserved. Signal only an already-proved owned process.

Keep bootstrap module exemptions pinned to approved module objects. The standard-library `__mp_main__` alias may refer only to the exact approved `__main__` object. Do not exempt a foreign module by its name or claimed file path. Prefer checked named-module execution over replacing the active main module when executing a service entry point.

Use the existing test catalog or project record. A second test database is not necessary.
Before RC execution, freeze a versioned mandatory manifest with these items:

- Critical baseline workflows.
- Applicable maintained regressions.
- Affected scenarios and workflows.
- Conditional checks for the change's risks.
- Test IDs, suite versions, shards, required resources, and acceptance criteria.

If impact is uncertain, select broader coverage.
An impact map helps selection. It does not prove that all effects are known.
Scheduled extended suites cannot replace applicable mandatory release checks.
Full gate means satisfactory execution of every mandatory item in the accepted manifest.
It does not mean every historical test or only the implementing agent's selected tests.

Bind results to candidate digests and applicable configuration, migrations, data, tests, and gate version.
Examine upstream dependency evidence as well as direct task results before combined acceptance.
Verify discovery and every shard's completion.
Use different result labels for failed, blocked, cancelled, missing, skipped, and flaky results.
Do not silently omit cases or accept zero discovered tests.
Unresolved flaky critical cases block acceptance.
For other exceptions, explicit project authority, policy, and follow-up records are necessary.
The optional delivery helper requires `passed` for every declared test.
For a gate that must check each reported case, use [original report checks](delivery.md#check-original-gate-reports) or an equivalent project control.
Give each mandatory case a stable ID and an exact test selector.
In the existing test catalog or defect record, keep the requirement or defect source for each case.
Before removal, record the accepted replacement or the reason why the case no longer applies.
For an accepted manifest change, create a new version and examine evidence applicability again.
Do not reduce the manifest to conceal failure.
Keep failed attempts even after a later pass.
If a required case did not pass, do not select or publish the candidate.
After a failed gate, [register and check a different candidate](delivery.md#use-a-new-registered-candidate-after-a-failed-gate) when you use the delivery helper.
Retirement preserves prior gate results. It does not make an incomplete or failed gate pass.
Recovered checks remain nonpassing when a late callback arrives. Obtain new evidence through a new actual check.
Before another attempt, find the cause and correct the applicable problem. Do not retry blindly.

## Bind the code that acceptance executes

When acceptance uses custom drivers, check the required dependency inventory before the first affected import or command.
An inventory supplied by a producer is not proof that all required files are present.
Check the actual runtime copies against their verified origins or archive, and check them again before recording success.

A source-file digest does not identify cached bytecode that an import can execute.
Load verified source bytes directly or use controlled execution trees and cache paths that enforce the accepted source identity.
The Python `-B` option prevents cache writes; it does not prevent cache reads.
Record the effective interpreter flags and cache controls.
Use explicit errors for integrity checks, or reject optimized execution before admission; Python optimization can remove `assert` statements.

Compute file digests from the actual written bytes.
If a normalized-text digest is useful, label it separately from the raw-file digest.
Preserve earlier records and add a dated correction instead of silently changing a frozen digest.

## Own the MCP service during local acceptance

For complete MCP shutdown evidence in local acceptance, keep ownership explicit.
The existing MCP server supports an explicit `owned-http` transport in addition to its compatible stdio default.
The independent executor starts that same service outside the Codex-owned process job; Codex connects directly to its authenticated loopback URL.
This adds neither a relay nor a fourth tool. Keep the required Hook proofs and independent CLI gate executor.

The executor supplies a fresh 64-hex `SDD_HARNESS_MCP_BEARER` only to the service and client environments.
The service removes that credential from its environment before gate subprocesses can inherit it.
Serve with `--transport owned-http --port 0`, retain the actual ready URL and process identity, and configure the client with the observed nonzero port.
The ready record and possession of the bearer are not acceptance evidence.
Keep the token value out of configuration files and retained records.

After the Codex client finishes, the independent executor closes its retained owner-stdin pipe and waits for the actual service.
Normal shutdown requires observed exit zero plus complete matching final self-verification; business results remain a separate requirement.
Unexpected owner input, unsolicited service return, write failure and recorded force termination cannot satisfy that condition.
An ASGI startup or shutdown failure remains an error even when the HTTP library returns without raising it.
Keep historical unknown causes unknown. Do not relabel a host-owned stdio force-stop as healthy or substitute a turn/SessionEnd checkpoint for final process evidence.

Keep the owner channel separate from the Git metadata queries in `coordination.checkout_origin`, `coordination.default_registry`, and `delivery.fingerprints`. These read-only Git children receive null stdin and retain all inherited Git configuration variables. The owner reader uses its own unbuffered duplicate descriptor, so a failed server does not leave the standard buffered input locked during interpreter exit. Verify a bind failure while the executor still holds the owner pipe open, as well as normal EOF drain.

## Bind actual acceptance descendants

An outer source-verification receipt does not bind a new interpreter automatically.
For formal dependency-binding evidence, the trusted executor must bind the actual independent CLI, registered verifier, isolation launcher, and generator before their custom code or dependencies execute.
Keep the expected entry digest, exact required inventory, candidate identity, interpreter policy, and dependency roots in a trusted launch contract.
Check the contract and first loader bytes before compilation. Compile controlled source bytes directly, reject custom bytecode, and reject optimized execution.
For native extensions, check the actual resolved file and loaded object. Do not exempt an entire Python package from source checks.

Keep child observations separate from the parent's receipt.
Retain role, process identity, launch-contract digest, actual dependency paths and digests, inherited Git fingerprints, and matching final evidence.
An observed child exit zero without the required final evidence is incomplete.
Keep checks active through Python shutdown callbacks before writing final proof.
The repository acceptance adapter rejects live background threads without a healthy ending; the target must join them before returning.
Its prepared command API is for ordinary subprocess launches. Pass raw argv through the guarded native launcher so that it selects low-writable self-record storage before sealing the contract.
Use isolated dependency copies for mutation checks. Verify that changed source or native dependencies cannot reach the payload.
Do not change shared dependencies or old frozen evidence to perform a negative check.

The restricted generator keeps inherited `GIT_*` values while it excludes gate credentials and report authority from its minimal environment.
Keep its low-integrity token, private work directory, protected destinations, and no inherited handles.
Explicit environment changes in a test retain their stated semantics; do not clear the host environment to obtain a passing result.
These checks establish the stated file and execution identities. They do not attest interpreter or OS builds or provide a hostile-code sandbox.

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
