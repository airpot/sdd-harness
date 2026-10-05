# Acceptance, Integration, and Publication

## Assess completion

Check each necessary acceptance condition against actual results and currently applicable evidence.
Distinguish implementation, task validation, combined acceptance, publication, and resource cleanup.
A filled template or a larger test count does not prove completion.
Write internal completion records according to [the writing policy](writing.md).

Use a fixed baseline and candidate for integration.
Check relevant interfaces and actual dependencies.
Check small combined changes early.
Incomplete unrelated tasks do not block the current scope.
Missing relevant dependencies still block acceptance.

If acceptance includes deployment, obtain deployment evidence.
Otherwise, do not require publication to complete development.

## Use the release entry

Read the existing release process, target environment, responsible role, and user authorization.
Prefer existing CI concurrency controls, approvals, or controlled host tools.
Check their actual configuration and pending runs.
Development chats provide candidates. They do not automatically have deployment authority.

Record the exact candidate commit, artifact hashes, necessary evidence, and target.
Use only the recorded candidate for this release.
Do not use passing evidence for commit A as unconditional evidence for commit B.
If acceptance conditions or specifications change, review evidence applicability.

If releases compete, old requests remain, or results are uncertain, check the release owner and actual target state.
Check the selected candidate.
Without a reliable exclusive release entry, do not claim that the skill prevents competing releases.
Do not use a new shared Git file or a custom lock as proof of release authority.
Prepare a reviewable candidate. Resolve the missing control through the existing project process.

If authorization and entry conditions hold, complete the release without repeated confirmation.
If release authorization is missing, first prepare a reviewable result.
Then obtain authorization for the specific external action.

Before release execution, record its run reference.
After execution, record the actual result and validation evidence.
Timeout, cancellation, or a closed window does not prove external failure or rollback.
Use the same run reference to determine the result.
Follow platform retry semantics. Do not deploy again without checking the previous result.

Use the [release template](../assets/release.md) only for the current scope and relevant dependencies.
Do not put credentials in handoff records or snapshots.
