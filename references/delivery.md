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
