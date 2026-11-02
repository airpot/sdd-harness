# Delivery Record

Writing policy: <accessible-writing-policy-reference>.
Before you keep this record, replace this placeholder with the project's policy reference or an installed skill policy.
Use this record's directory at its destination as the base directory for local links. Make sure that the next reader can read the policy.
Keep the project's format, identifiers, and raw evidence.
Use only fields that are applicable to the scope at delivery.

For applicable fields, use these instructions:

- Scope: give references to tasks and related dependencies.
- Candidate: record the identities of the integrated commit, specification version, build run, build artifacts, and hashes.
- Candidate basis: identify applicable configuration, migrations, test data, tests, and the immutable manifest hash.
- Integration target: give references to its version at integration and validation of the combined candidate that it receives.
- Optional cooperation: give references to the accepted shared contract and full workflow evidence for the combined candidate.
- Acceptance: give references to evidence for each condition and combined validation.
  Put work without verification in a different group.
- RC gate: identify the environment slot, owner, deployment receipt, gate version, mandatory test IDs, and completed shards.
  For a continuing candidate, keep slot ownership until all mandatory gates and evidence capture are completed.
  Keep failures, cancellations, skips, flaky results, missing results, and accepted exception authority.
- Verdict: record scope with acceptance for all conditions, acceptance for some conditions, or `blocked` results.
  Identify each mandatory condition with a `failed`, `blocked`, or `not run` result.
- Evidence applicability: record applicability at delivery and the reason that evidence from before the change is applicable.
- Validation recipe: give references to steps that the reader can do again, necessary inputs, environment, and pass criteria.
- Specification reconciliation: give references to the record with specification authority and accepted updates. Write each remaining closure gap.
- Release: identify the entry that the project uses, environment, owner, and authorization.
  Identify runs that can have conflicts or runs without completed execution.
- Eligibility: record the selected candidate at execution, supersession check, and conclusion at execution.
  Include the expected and returned selection generations and expected target revision.
- Operational conditions: identify applicable rollout observations, stop conditions, recovery authority, and configuration or data compatibility.
- Execution and result: record the run reference, start and observation times, result from execution, and environment validation.
  Include the idempotency request ID, receiver checks, observed artifact digests, and outcome reconciliation.
- Cleanup: identify temporary worktrees, activity checks, kept results, recovery validation, and native removal results.
- Candidate withdrawal: identify current authority, stopped-writer observations, actual external outcome, retained history, and released resources.
  Keep retirement, failed checks, verification, and rollback as different results.
- Follow-up: write conditions that prevent progress or identify tasks for subsequent execution.
