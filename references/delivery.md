# Acceptance, Integration, and Publication

## Examine completion

Examine each necessary acceptance condition with results and evidence that are applicable at this time.
Keep scope, status, and approval for each operation: implementation, task validation, combined acceptance, publication, and resource cleanup.
Content in a template or a larger test count is not sufficient evidence of completion.
Obey [the writing policy](writing.md) for completion records for project development.

Examine source requirement coverage with [specification review](spec-review.md).
Do not examine only conditions from a task list that does not include all source requirements.
Before you give a report of full acceptance, each necessary condition must have applicable evidence of a pass.
If a necessary check is not satisfactory, give a report of its condition without acceptance.

If a necessary check has a blocker or no execution, give a report of necessary acceptance conditions without satisfactory evidence.
Give these conditions and their effects on the verdict.
Do not put a mandatory condition without acceptance in a footnote below a success verdict.

Keep the source and scope for implementation status and acceptance status.
Record the applicable scope verdict: accepted, partial, or blocked.
If the project gives verdict terms, use them.
If the project gives no verdict terms, use these meanings:
Accepted: all necessary conditions have applicable evidence of a pass.
Partial: only specified parts are accepted.
Blocked: a necessary condition without a decision prevents completion of the specified scope.

Keep conditions and scopes for results that are not satisfactory, blockers, and checks without execution.
Keep the aggregate scope verdict.
For exclusions with project authorization, give the authority, source evidence, scope, and effects that continue.
Do not remove a necessary condition from acceptance only to get a success verdict.

Make sure that validation records give executable steps, necessary inputs and environment, pass criteria, results, and source references.
For previous evidence that you use again, record if it is applicable at this time.
Record the information that makes this evidence applicable.
A previous satisfactory result without a check of its applicable conditions is not sufficient evidence of acceptance at this time.
Before closure, examine reconciliation of the specification with project authority with [the workflow](workflow.md).


For integration, select one baseline and candidate.
Keep their identities the same.
When you select this baseline and candidate, obey [integration with the target at integration](workflow.md).
Examine related interfaces and dependencies directly.

Do checks of small combined changes before large integration batches.
Tasks that are not included in this scope and have work that is not completed do not prevent acceptance of this scope.
Missing related dependencies prevent acceptance.

If acceptance includes deployment, get deployment evidence.
If acceptance does not include deployment, publication is not necessary to complete development.

## Keep one RC candidate

Before merge, validate the current combination with the integration target.
After combination changes that affect the evidence, examine its applicability.
Build the release candidate (RC) from a fixed integrated commit.
Record artifact digests and the applicable specification, configuration, migrations, test data, and gate identities.
Keep these identities immutable for the candidate.
If an identity that affects candidate evidence changes, register a new candidate.
For that new candidate, examine necessary checks again.
Promote the tested artifacts by digest. Evidence for a rebuild is necessary even with the same commit.

Use candidate-specific resources when possible.
For a shared RC, reserve the actual environment and database before deployment.
For a continuing candidate, keep the slot until every mandatory gate and evidence capture are completed.
Do not release the slot immediately after deployment.
For withdrawal, use the explicit retirement procedure below.
For full gate scope and test admission, use [testing rules](testing.md#freeze-the-full-gate).

The optional [local registry](coordination.md) also supports `scripts/delivery.py` with Python standard-library modules.
Use the project's existing release record when it supplies equivalent controls.
The [candidate example](../assets/candidate.example.json) shows the helper's manifest structure.
Replace every placeholder and digest with actual project values before registration.
Include applicable configuration, migrations, data, tests, and accepted specifications in `basis`.
Include project runner files and their applicable dependencies in `basis`.
Record the gate version in a basis file.
Freeze each gate's full test list.
The example commands are placeholders for project runners, not installed skill commands.
Keep secrets out of arguments, basis files, receipts, and retained logs.

For an authorized project with a completed manifest, the helper sequence is:

```text
python <skill>/scripts/delivery.py --root <project> register --manifest <candidate.json>
python <skill>/scripts/delivery.py --root <project> run --candidate rc-17 --stage rc --request rc-17-deploy
python <skill>/scripts/delivery.py --root <project> run --candidate rc-17 --stage gate --gate system --request rc-17-system
python <skill>/scripts/delivery.py --root <project> select --candidate rc-17 --expected <current-selection-generation>
python <skill>/scripts/delivery.py --root <project> run --candidate rc-17 --stage publish --request rc-17-publish --selection <returned-generation> --authority <authority.json>
python <skill>/scripts/delivery.py --root <project> run --candidate rc-17 --stage verify --request rc-17-verify --selection <returned-generation> --authority <authority.json>
```

Run every named gate before selection. The example has one gate.
Use `inspect` to find the current selection generation. An absent selection has generation zero.
Selection uses compare-and-set semantics. A stale expected generation cannot replace the current selection.
You can keep the selected candidate fixed. The newest commit is not mandatory for this selection.

The project runner must examine the actual deployed artifacts.
Then, it must return a structured receipt.
A successful process exit alone cannot satisfy a gate.
The runner writes its receipt to `SDD_GATE_RESULT` and identifies the candidate and observed artifact digests.
For gates, its `tests` map must contain exactly the declared test IDs with `passed` results.
Do not convert skipped or flaky results into passes.
For publication, the receiver must check the expected target revision before mutation.
Publication receipts identify the previous target revision and the observed new candidate revision.
Verification receipts identify the target, candidate revision, and observed artifacts.

The frozen authority file records the project's existing authorization. Its fields give no credentials or native permissions.
Use the manifest's actual candidate, target, and observed target revision:

```json
{
  "authorized": true,
  "candidate": "rc-17",
  "target": "production:app",
  "target_revision": "<observed-target-revision>"
}
```

Participating CI jobs must use the same authority and resource keys for the actual target.
Separate CI runners do not automatically share this local registry.
Use verified CI controls or a project backend for their shared targets.
Keep merge validation and deployment serialization as separate controls.

For participating GitHub Actions workflows, use one concurrency group for the production target that these workflows share.
This fragment queues deployments without cancellation of an active mutation:

```yaml
concurrency:
  group: app-production
  queue: max
  cancel-in-progress: false
```

Use the same group across all workflows that modify that target in the repository.
Before use, examine support in the selected GitHub version and the actual project workflow.
This group does not coordinate different repositories or commands outside Actions.
For GitLab, use the project's target-specific `resource_group` and outdated-deployment controls.
Until its gates are completed or authorized retirement resolves the candidate, keep the RC slot.
A production-only group cannot protect a shared RC.
Sources: [GitHub concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
and [GitLab deployment safety](https://docs.gitlab.com/ci/environments/deployment_safety/).

## Resolve candidate operations

Keep one request ID for each operation.
Repeated requests with the same ID retrieve its recorded state without another mutation.
Do not use a new ID to retry an uncertain operation.
Examine the actual runner, descendants, resource state, and external outcome first.
Keep target serialization until the outcome has resolution.
For recovery, use `reconcile --request <request-id> --evidence <resolution.json>` with `--root <project>`.
The recovery record must identify actual stopped-writer observations and the resolved external outcome.
Keep the initial failure and the recovery evidence.
After a failed gate, use a new candidate. Do not silently replace a failure with a pass.
Before reconciliation, confirm stopped writers.
Before a new candidate uses the slot from the failed operation, reconcile that operation.

A successful RC recovery uses this structure with actual observations and artifact digests:

```json
{
  "writer_stopped": true,
  "outcome": "passed",
  "observations": "<native writer observations and actual external result reference>",
  "receipt": {
    "candidate": "rc-17",
    "artifacts": {"app": "sha256:<actual-64-hex-digest>"}
  }
}
```

For a gate recovery, include the full `tests` map in its receipt.
For publication or verification recovery, include the target fields from the applicable stage contract.
For a failed outcome, use `"outcome": "failed"` with actual stopped-writer and outcome observations.
That outcome releases the candidate's slots and prevents its acceptance.
The helper records the writer-stop assertion. It cannot determine native termination from the JSON fields.
Apply the [wrapper and writer conditions](coordination.md#return-recover-and-close) before recovery.
After explicit resolution, later callbacks cannot replace that resolution or release a successor's resources.

The receiving release entry must enforce current selection, authorization, target revision, and idempotency.
A stored selection can still name a retired candidate. The receiver must reject that candidate before mutation.
Native credentials and permissions determine bypass protection.
Local registry checks and hook prose cannot enforce an external receiver.

## Retire a candidate

If a candidate cannot continue after an accepted change or withdrawal decision, examine its actual operations and external state.
A successful earlier stage remains a historical success. Do not manufacture a failed gate to release its resources.
Resolve running or uncertain operations first. Retirement does not cancel a process or resolve an unknown external effect.
Find current project authority for withdrawal. Obsolete publication authority is not sufficient or necessary for that different action.

Use a new project-relative authority file with this structure and actual identities:

```json
{
  "authorized": true,
  "action": "retire",
  "candidate": "rc-17",
  "target": "production:app",
  "manifest_sha256": "sha256:<registered-manifest-hash>"
}
```

Use `inspect` to find the registered manifest hash. Inspection does not create storage or change coordination policy.
Record actual stopped-writer observations and the observed external outcome in an evidence file:

```json
{
  "format": 1,
  "candidate": "rc-17",
  "target": "production:app",
  "manifest_sha256": "sha256:<registered-manifest-hash>",
  "authority": "withdrawal-authority.json",
  "writer_stopped": true,
  "writer_observations": "<actual command, descendant, and wrapper observations>",
  "external_outcome": {
    "status": "unchanged",
    "target_revision": "<observed-prior-target-revision>",
    "observations": "<actual target observation and source>"
  },
  "reason": "<accepted change or withdrawal decision reference>"
}
```

Use `unchanged`, `published`, `removed`, or `restored` for the observed outcome.
For `unchanged`, set `external_outcome.target_revision` to the registered manifest's `target_revision`.
For `published`, set it to the candidate ID, such as `rc-17`.
For `removed` or `restored`, record the actual project revision that identifies the observed state.
No unknown outcome permits retirement. These fields record project assertions, not independent provenance or native permissions.

```text
python <skill>/scripts/delivery.py --root <project> retire --candidate rc-17 --evidence retirement.json
```

The helper retains the evidence, current authority bytes, and prior stage records.
It releases only resources owned by this resolved candidate.
A retired candidate cannot start a new stage or receive selection.
The same retirement evidence returns its original record. Different replacement evidence is rejected.
An identical previous operation request can still retrieve its historical result without another mutation.
Use the current selection generation to select an eligible successor.
Observe the actual target revision for that successor. Retirement does not verify a release or roll back the target.

## Use the release entry

Read the release process, target environment, role with release authority, and user authorization that the project uses.
If CI concurrency controls, approvals, or host tools with controls are available, use them.
Examine their configuration and runs that are not completed directly.
Development chats supply candidates.
They do not automatically have deployment authority.

Record the candidate commit, artifact hashes, necessary evidence, and target to identify this release.
Use only the recorded candidate for this release.
Before you use evidence for commit A for commit B, examine its applicable conditions.
If acceptance conditions or specifications change, examine if the evidence is applicable.

If requests are in conflict, do the owner and target-state checks.
If previous requests are not completed or outcomes are unknown, do these checks.
Examine the release owner and target state directly.
Examine the selected candidate.

At execution, examine the candidate that the release system selects at this time and its supersession rules.
If release supersession removes this request's publication eligibility, reject it or get a decision with this system before publication.
Exclusive execution is not sufficient evidence that the candidate continues to have eligibility.

Before a decision for a request with supersession from the selected release, examine operation semantics.
Cancellation or rejection of a queued request and an attempt at its deployment are different.
Do not send a deployment request with supersession from the selected release only to examine the system's rejection behavior.
If no cancellation operation has approval, keep the request.
Give a report of the condition that prevents permitted execution.

Commit dates and previous chat authorization are not sufficient evidence of eligibility.
Keep these as different operation types: a rollback with project approval and publication of a candidate with supersession.
Use the project's process and specified authority for a rollback with selection from project authority.

If the entry cannot prevent releases at the same time, do not give a report that the skill can.
Do not use a new Git file for shared state as evidence of release authority.
Do not use a lock from a specified project procedure as evidence of release authority.
Prepare a candidate that a reviewer can examine.
Get the missing control with the project's procedure.

If authorization is applicable and the release agrees with entry conditions, complete the release without confirmation again.
If release authorization is missing, first prepare a result that a reviewer can examine.
Then, get authorization for the specified external action.

Before release execution, record its run reference.
For publication with risk, find rollout scope, success signals, stop conditions, and the role that must make the recovery decision.
Examine configuration and data compatibility for the recovery path in the proposal.
If a necessary recovery condition has no decision, do not do publication.
Use the project's deployment and recovery process.

Publication authorization does not automatically give authorization for production experiments or different recovery actions.
Record environment validation and recovery outcomes from execution.

After execution, record the result and validation evidence from that execution.
A timeout, cancellation, or closed window is not sufficient evidence of external failure or rollback.
Use the same run reference to find the result.
Obey platform retry semantics.
Before deployment again, examine the previous result.

Use the [release template](../assets/release.md) only for this scope and related dependencies.
Do not put credentials in handoff records or snapshots.
