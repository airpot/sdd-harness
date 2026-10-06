# SDD Harness Behavior Specification

Specification version: 0.4.0.
Status: accepted intent for the six improvements in the 0.4.0 revision.
This specification defines observable skill behavior. It does not establish host enforcement.

## Scope

Keep the package portable across chats, worktrees, machines, and coding agents.
Use project specifications, task records, Git, and verified host tools.
Do not require a new coordination service or database.
Keep routine actions within existing user authorization.

## Requirements and validation

| ID | Required behavior | Validation reference |
| --- | --- | --- |
| SDD-1 | Check specification ambiguity, conflicting contracts, boundaries, failure scenarios, assumptions, and non-goals. | `conflicting-contract`; specification review reference. |
| SDD-2 | Trace source requirements through acceptance conditions, work, implementation, and evidence. Identify omissions and unsupported added behavior. | `omitted-requirement`; change record and review. |
| SDD-3 | Required conditions need applicable passing evidence for complete acceptance. Preserve blocked, failed, and unrun results. | `required-check-blocked`; acceptance rules. |
| SDD-4 | Record runnable validation steps, necessary inputs, environment, pass criteria, results, and evidence applicability. | `stale-evidence`; evidence records. |
| SDD-5 | Reconcile accepted changes with the project's authoritative specification and affected artifacts. | `living-spec-reconciliation`; `historical-spec-reconciliation`. |
| SDD-6 | Keep small tasks brief. Reuse existing IDs, records, formats, and authorization. | `small-change`; both reconciliation scenarios. |
| SDD-7 | Review assertion meaning against accepted expected results. Use useful counterexamples, defect reproduction, and preservation checks. | `incorrect-test-oracle`; `bug-preservation`. |
| SDD-8 | Check the current integration target. Validate the actual combined candidate after relevant target or dependency changes. | `advanced-integration-target`; `advanced-target` host fixture. |
| SDD-9 | Check release eligibility at execution. Resolve superseded requests through the existing release system. | `obsolete-release-candidate`; `obsolete-release` host fixture. |
| SDD-10 | Select checks by affected behavior and risk. Check applicable performance, security, data compatibility, rollout, and authorized recovery. | `migration-recovery`; `performance-acceptance`; instruction review. |
| SDD-11 | Ground technical planning in relevant current code and decisions. Reuse existing components and preserve accepted behavior. | `brownfield-reuse`. |
| EVAL-1 | Retain original cases and expand collaboration and recovery evaluations. Grade actual action outcomes and repeat fresh trials. | Expanded scenarios and criteria; repository-only host evaluations. |
| GUARD-1 | Keep unknown activity distinct from idle state. Preserve active worktrees and unresolved ownership. | Existing collaboration rules; inspect regression tests. |
| GUARD-2 | Keep development, acceptance, publication, removal, and chat archives distinct. | Delivery and recovery review; source-preservation tests. |
| DOC-1 | Use English and STE-guided writing for internal prose. Preserve language exceptions and exact source strings. | Writing reference; prior 0.2.0 language evaluations. |
| PACK-1 | Install the complete package without overwriting different content. Preserve portable links and checked distributions. | Installer and package tests. |

## Acceptance rules

Evaluate SDD requirements against the saved scenarios and actual answers.
Include busy entry, unknown activity, returning executors, failed removal retry, and renewed writer activity in guard evaluations.
Run one baseline host trial and three fresh forward trials, each with four isolated cases.
Grade journals, actual files, hashes, and executable behavior separately from executor prose.
An unsafe attempted action remains a failure even when the simulated host denies it.
Read evidence and source artifacts directly for instruction review.
Keep package test results separate from behavioral evaluation results.
Inspect unchanged guards when changing shared instructions.
Do not infer full-standard STE compliance from sentence counts.

## Specification maintenance

Maintain this file as the living contract for the skill.
Record accepted behavior changes here before final acceptance.
Keep released packages and versioned evaluation results for historical comparison.
If evaluation exposes an implementation gap, correct the instructions or record incomplete acceptance.
Do not weaken a requirement merely to obtain a passing result.

## Evidence locations

Inputs: [evals/scenarios.json](../evals/scenarios.json).
Criteria: [evals/criteria.json](../evals/criteria.json).
Expanded inputs: [evals/scenarios-0.4.0.json](../evals/scenarios-0.4.0.json).
Expanded criteria: [evals/criteria-0.4.0.json](../evals/criteria-0.4.0.json).
Procedure: [evals/README.md](../evals/README.md).
Host operation reference: [evals/host-README.md](../evals/host-README.md).
Host regression tests: [tests/test_eval_host.py](../tests/test_eval_host.py).
Tool regression tests: [tests/test_skill_tools.py](../tests/test_skill_tools.py).
Package tests: [tests/test_package.py](../tests/test_package.py).

Evaluation results are not host controls.
Evaluation tools remain outside the installed skill and release ZIP.
Fixture ownership, selection, and authorization controls are simulated. Actual files, hashes, and executable checks run locally.
Live runtime behavior across all products, machines, and operating systems remains unverified.
