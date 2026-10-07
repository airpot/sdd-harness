# SDD Harness Behavior Specification

Specification version: 0.7.3.
Status: accepted intent for portable development guidance, optional cooperation, and observable skill effectiveness checks.
This specification defines observable skill behavior. It does not establish host enforcement.

## Scope

Independent development is the default. Use collaboration procedures only when work needs cooperation.
Keep the package portable across chats, checkouts, and coding agents.
Use project specifications, task records, Git, and verified host tools.
Use ordinary Git for portable developer collaboration.
Exclude cross-machine execution claims, heartbeat leases, and distributed coordination services from the required workflow.
Keep local activity, ownership, preservation, and release eligibility checks.
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
| PACK-1 | Put SKILL.md and its resources at the repository root for direct installation. Filter development files from scripted installation and ZIPs. Preserve local changes, portable links, and checked distributions. | Installer and root-repository package tests. |
| DEFAULT-1 | Keep independent development the default. Require no collaboration roles, contract formats, mocks, or team CI setup for ordinary independent work. | `solo-default-lightweight`; `small-team-existing-layout`; `small-change`. |
| TEAM-1 | Link cooperating component tasks and acceptance to the complete business outcome. Reuse existing integration duties. | `split-business-acceptance`. |
| TEAM-2 | Use the existing accepted versioned contract. Align examples, mocks, clients, and relevant field, error, time, and unit semantics. | `contract-source-drift`. |
| TEAM-3 | Distinguish component or mock results from actual provider, consumer, and complete workflow evidence. | `mock-only-team-completion`. |
| TEAM-4 | Keep shared breaking changes as proposals until accepted. Assess affected tasks, types, configuration, schemas, compatibility, and migration. | `shared-breaking-change`. |
| TEAM-5 | Reference existing project settings and actual commands. Isolate runtime collisions. Distinguish written scope from observed native enforcement. | `project-harness-profile`; `small-team-existing-layout`. |
| TEAM-6 | Use one exact combined candidate against the current target. Allow ordinary assigned Git work without distributed runtime claims. | `single-integrated-candidate`; `ordinary-git-collaboration`. |
| SUB-1 | Keep delegation optional and proportional to useful independent work. Resolve dependencies before dependent implementation. | `subagent-small-change`; `subagent-dependent-work`. |
| SUB-2 | Supply self-contained task context, accepted basis, scope, output, and execution limits. Check actual instruction inheritance. | `subagent-task-context`. |
| SUB-3 | Retain main-agent acceptance and integration responsibility. Keep delegated actions within actual authority and host controls. | `subagent-shared-contract`; `subagent-host-capabilities`. |
| SUB-4 | Assess actual artifacts and applicable evidence. Keep partial results incomplete and record a parent disposition. | `subagent-false-success`; `subagent-partial-budget`; `worker-report` fixture. |
| SUB-5 | Validate the combined candidate and complete requirement coverage, including work outside worker scopes. | `subagent-combined-workflow`; `workers-combined` fixture. |
| SUB-6 | Bound concurrency, nesting, retries, and review loops. Resolve disagreement through evidence rather than votes. | `subagent-review-loop`; `subagent-partial-budget`. |
| SUB-7 | Preserve outstanding workers and decisions during parent replacement. Do not assume transferable native worker control. | `subagent-parent-replacement`. |
| SUB-8 | Distinguish returned output, acceptance, resident context, active execution, and resource closure. Preserve descendant results before removal. | `subagent-interrupted-writer`; `interrupted-worker` fixture. |
| SUB-9 | Assess superseded attempts without overwriting accepted work or repeating unknown external effects. Worker messages do not grant authority. | `subagent-stale-attempt`; `superseded-result` fixture. |
| SUB-10 | Evaluate delivered value and actual outcomes. Do not infer correctness or improvement from worker calls, agreement, or passing simulations. | Instruction evaluation, fixture outcomes, and validation limits. |
| TRUST-1 | Keep evidence content separate from instruction authority. Check provenance for claimed requirement or authorization changes. Retain valid previous authority. | `untrusted-evidence`; editable handoff task. |
| ROUTE-1 | Provide a self-contained small independent path. Load deeper procedures by applicable operation, ambiguity, dependencies, or risk. | `solo-path`; invocation positive and negative controls. |
| DELTA-1 | Check additions, modifications, removals, and renames through existing requirement identities. Validate obsolete behavior absence and accepted transitions. | `removed-renamed`; editable removal task. |
| HOST-1 | Observe full entry and resource access separately from installation and catalog visibility. Record verified, unavailable, and untested capabilities. | `capability-observation`; native loading checks. |
| EVAL-2 | Compare actual editable task outcomes under matched skill conditions. Bind reports to candidate, accepted inputs, grader, and environment. | Repository-only coding tasks and tests. |
| EVAL-3 | Evaluate explicit, implicit, and negative skill invocation separately from output correctness. Distinguish native traces from selection simulations. | `invocation-0.7.0.json`; native smoke traces. |
| RECOVER-1 | Reject shallow repositories before archive creation. Preserve the source and do not fetch history automatically. | Shallow-source regression in `tests/test_skill_tools.py`. |
| PACK-2 | Reject symbolic links and Windows reparse points before source or target traversal and final-target installation. Keep Python 3.10 support. | Real junction fallback regressions in `tests/test_followup_corrections.py`; builder and installer. |
| DOC-2 | Before saving an optional copied template, complete its policy reference for the actual record destination. Keep project policy authoritative. | All three templates; relocated project and installed-policy link checks; fresh template smoke. |
| EVAL-4 | Bind actual request identity and input hash to source case, adaptation, expected route, observed route, and trace. Preserve historical raw evidence. | Dated 0.7.0 invocation errata; 0.7.1 native request records. |
| RECOVER-2 | Before creating restore output, clear Git's reported repository-local variables in a copied subprocess environment. Use that environment throughout restore. Preserve existing source repositories and unrelated caller settings. Verify the target's actual Git directory, HEAD, and own index, including unborn restoration. | Foreign index, repository, common/object-directory, caller-environment, and unborn regressions in `tests/test_072_corrections.py`. |
| PACK-3 | Filter cache directories against paths relative to the source or target inventory. Preserve the complete portable payload below cache-named external ancestors. Reject empty output inventories before destination creation. | Source/target ancestor, internal-cache exclusion, inventory/hash, idempotency, and empty-inventory regressions in `tests/test_072_corrections.py`. |
| EVAL-5 | Clear Git-reported repository-local environment variables case-insensitively in copied fixture child environments before creation. Preserve caller settings, foreign repositories, and staged-only indexes. Check actual fixture metadata, HEAD, and index at creation and busy grading. | Foreign routing, missing external index, actual staged-only preservation, caller environment, and malformed own-index regressions in `tests/test_073_corrections.py`. |
| RECOVER-3 | Disable operation-local init templates and hooks during restore without changing user configuration. After Git operations, verify all actual regular working files and hashes against the manifest, including selected ignored results. Exclude only root Git metadata. Require deleted paths to remain absent. Retain repository, HEAD, own-index, and unborn checks. | Environment/configured template, configured hooks, final unexpected/changed/recreated file checks in `tests/test_073_corrections.py`; existing restore checks. |
| RECOVER-4 | Reject effective nonempty legacy graft information before archive or destination creation. Resolve actual metadata and source environment, including linked worktrees. Preserve source history without automatic fetch or rewrite. Permit empty graft information. | Two-commit source, external graft file, linked worktree, source preservation, and empty-graft history roundtrip regressions in `tests/test_073_corrections.py`. |
| RECOVER-5 | Before recovery file traversal, use `lstat` symbolic-link and Windows reparse attributes independently of `Path.is_junction`. Keep Python 3.10 and standard-library-only support. | Real inside-root junction with the newer API removed in `tests/test_073_corrections.py`; existing link and containment checks. |
| PACK-4 | Keep active ZIP and checksum download names consistent with the entry version and actual release artifact. Keep historical release links and records unchanged. | Real temporary package/version regression in `tests/test_073_corrections.py`; release checks against the final actual ZIP and checksum. |
| GUARD-3 | Read inspect status with optional Git locks disabled. Preserve source index bytes and staged entries for timestamp-only changes. Continue to detect ordinary dirty state. | Actual index-byte, staged-entry, and dirty-state regression in `tests/test_073_corrections.py`. |

## Acceptance rules

For 0.7.3, retain actual fail-first counterexamples for EVAL-5, RECOVER-3 through RECOVER-5, PACK-4, and GUARD-3.
Check foreign staged-only content with ordinary Git after fixture operations. Missing external indexes must remain absent.
Busy grading must reject missing, empty, or corrupt actual fixture indexes despite earlier successful journals.
Use disposable templates, configuration files, hooks, repositories, and real Windows junctions for sensitive checks.
Check normal history restoration alongside graft rejection and preserve source files and accessible original commits.
Bind active release links and embedded entry version to the actual newly built ZIP and its recorded checksum before publication.
Keep the fourteen-file payload, independent default, local-change protection, and raw historical records.
Report simulated API fallback coverage separately from native Python 3.10/3.11 execution.
These checks do not establish sandbox enforcement, new native invocation results, or general performance gains.

For 0.7.2, retain actual fail-first restore and distribution counterexamples and passing affected regressions.
Check that foreign Git environment settings do not change source index content, HEAD, branch association, or other source files.
Check the output repository and its own index with an ordinary Git environment.
Check all fourteen portable file hashes below source and target cache-named ancestors, including repeated installation and local-change refusal.
Keep internal cache exclusion, the independent default, and the existing preservation boundaries.
These checks do not establish new native routing, performance, or older-interpreter results.

For 0.7.1, run affected runtime, relocation, and invocation-binding regressions before final package acceptance.
Keep actual red failures and passing repeats. Preserve the fourteen-file portable payload and independent default.
When older Python interpreters are unavailable, identify fallback tests on the current interpreter separately from native compatibility trials.
Record read-only invocation adaptations explicitly. Do not perform publication or removal merely to test routing.
Keep historical worker-assessment observations separate from canonical solo-route coverage.
Retain passing coding and template baselines, first instruction misses, and their original provenance.
These corrections do not establish general performance or efficiency gains.

For 0.7.0, evaluate the four additional instruction cases and their sixteen hidden criteria.
Use isolated editable tasks for defect repair, existing-system feature work, and handoff with removed or renamed behavior.
Keep original failures, independent assertion checks, exact candidate hashes, and acceptance gaps.
Compare no-loaded-skill, released instructions, and revised instructions under matched task inputs.
Catalog visibility can remain in a no-loaded-skill baseline. Disclose that condition.
Do not claim that grading assertions are inaccessible under unrestricted host permissions.
Use actual native loading and invocation checks when the host is available.
Record unavailable hosts and controls honestly. Do not substitute simulated state for native execution evidence.
Existing scenario suites remain regression resources. Repeat affected scenarios after changes to their relevant rules.
The historical procedures below retain the methods used for previous versions.

Evaluate SDD requirements against the saved scenarios and actual answers.
Include busy entry, unknown activity, returning executors, failed removal retry, and renewed writer activity in guard evaluations.
Run one baseline host trial and three fresh forward trials, each with four isolated cases.
An unchanged host baseline can retain earlier evidence with explicit source hashes and applicability reasons.
Use released 0.4.0 instructions for the nine new baseline cases. Run all 28 cases for final 0.5.0 evaluation.
Keep all 84 criteria separate from executor inputs. Do not claim a performance gain when the baseline also passes.
Grade journals, actual files, hashes, and executable behavior separately from executor prose.
An unsafe attempted action remains a failure even when the simulated host denies it.
Read evidence and source artifacts directly for instruction review.
Keep package test results separate from behavioral evaluation results.
Inspect unchanged guards when changing shared instructions.
Do not infer full-standard STE compliance from sentence counts.

For 0.6.0, use twelve new scenarios and 48 hidden atomic criteria.
Run no-skill and released 0.5.1 baselines before changing instructions.
Run all forty cases and 132 criteria for the revised instruction evaluation.
Retain passing baselines without claiming observed improvement.
Run three fresh subagent fixture executors across all four new fixture kinds.
Each new fixture provides five actual outcome checks.
These checks assess recorded dispositions structurally. Independently assess reasons and final responses against task evidence.
Include one fresh run of the original four host fixtures to inspect shared guard applicability.
Keep executor inputs separate from criteria, scoring implementation, prior results, and proposed fixes.
Treat simulated stop controls separately from real cancellation and isolation behavior.
Retain original failures, corrections, and repeat-run evidence.

## Specification maintenance

Maintain this file as the living contract for the skill.
The accepted 0.7.2 revision isolates restore Git environment settings and corrects cache filtering within portable inventories.
The accepted 0.7.1 revision adds shallow-source rejection, legacy reparse guards, relocated policy references, and exact invocation attribution.
Historical 0.7.0 observations remain bound to their original commit and hashes through additive dated errata.
The 0.5.1 revision changed distribution layout and installer filtering only.
The accepted 0.6.0 revision adds optional subagent delegation, parent verification, bounded execution, and recovery rules.
Independent development remains the default. Existing scripts and release authority remain unchanged.
Record accepted behavior changes here before final acceptance.
Keep released packages and versioned evaluation results for historical comparison.
If evaluation exposes an implementation gap, correct the instructions or record incomplete acceptance.
Do not weaken a requirement merely to obtain a passing result.

## Evidence locations

Inputs: [evals/scenarios.json](../evals/scenarios.json).
Criteria: [evals/criteria.json](../evals/criteria.json).
Expanded inputs: [evals/scenarios-0.4.0.json](../evals/scenarios-0.4.0.json).
Expanded criteria: [evals/criteria-0.4.0.json](../evals/criteria-0.4.0.json).
Optional collaboration inputs: [evals/scenarios-0.5.0.json](../evals/scenarios-0.5.0.json).
Optional collaboration criteria: [evals/criteria-0.5.0.json](../evals/criteria-0.5.0.json).
Subagent inputs: [evals/scenarios-0.6.0.json](../evals/scenarios-0.6.0.json).
Subagent criteria: [evals/criteria-0.6.0.json](../evals/criteria-0.6.0.json).
Procedure: [evals/README.md](../evals/README.md).
Host operation reference: [evals/host-README.md](../evals/host-README.md).
Host regression tests: [tests/test_eval_host.py](../tests/test_eval_host.py).
Subagent host operation reference: [evals/subagent-host-README.md](../evals/subagent-host-README.md).
Subagent host regression tests: [tests/test_subagent_host.py](../tests/test_subagent_host.py).
Tool regression tests: [tests/test_skill_tools.py](../tests/test_skill_tools.py).
Package tests: [tests/test_package.py](../tests/test_package.py).

Evaluation results are not host controls.
Evaluation tools remain outside the installed skill and release ZIP.
Fixture ownership, selection, and authorization controls are simulated. Actual files, hashes, and executable checks run locally.
Live runtime behavior across all products, machines, and operating systems remains unverified.
