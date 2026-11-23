# Project MCP Service

Managed acceptance requires one local MCP service and two [native Codex Hook events](hooks.md). Stdio is the default transport. For explicitly executor-owned HTTP, use the [independent service procedure](testing.md#own-the-mcp-service-during-local-acceptance). Both transports keep the existing [delivery CLI](delivery.md), required Hook proofs, and independent verifier. The service and Hooks give a generator no new release authority.

| Tool | Action |
| --- | --- |
| `task_status` | Read a task and its next action. |
| `candidate_status` | Read a candidate, its checks, and its evidence state. |
| `request_gate` | Request one approved, registered format 3 gate. The only inputs are `candidate_id`, `check_name`, and `request_id`. |

Use the [independent acceptance procedure](delivery.md#separate-generation-and-acceptance).
Start the service from a trusted host. Keep the service script, policy, registry, verifier, and report paths outside the generator's write scope.
The native Hook records the active session and this call. The service uses that record to admit a one-use request through the delivery CLI.
The registered verifier runs the check and writes the official receipt and JUnit. The CLI retains the report digest and admission record.
Do not use MCP or a Hook to replace the host's write restrictions.

## Approve registered gates

Register the candidate through the delivery CLI. Use the candidate's ID, registration ID, manifest SHA256, and approved gate names.
Get the registration ID and manifest digest from [candidate inspection](delivery.md#inspect-a-known-candidate).
Keep the approval JSON in the trusted project. For example:

```json
{
  "rc-17": {
    "registration_id": "00000000000000000000000000000000",
    "manifest_sha256": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "checks": ["system"]
  }
}
```

Replace the example values with the actual registration and check names.
Keep the existing RC step. A gate request cannot register, stage, select, or publish a candidate.
For a changed policy, stop the old server, examine the change, and start the reviewed server.
Do not let the generator modify the policy or supply a command or report.

## Configure the project

Use a Python with MCP SDK 2.3.0 to start the server. The status and delivery CLIs do not need this package.
Use the verifier's Python with the registered check dependencies. On Windows, the local permission boundary can also require `pywin32` for the verifier's generator launcher.
From the MCP Python, print a Codex project configuration fragment:

```text
python -B <skill>/scripts/mcp_server.py configure --repo <project> --policy <trusted-project-policy.json> --gate-python <verifier-python>
```

Review and add the fragment to the trusted project's `.codex/config.toml`. The command only prints the fragment.
The fragment forwards the currently inherited Git variable names through `env_vars`;
it does not embed their values or clear overrides. Regenerate and review it if
the host introduces different environment variable names. The Hook and service
both retain the [Git configuration identity checks](coordination.md#inherited-git-configuration).
Use the host's tool approval procedure for `request_gate`. The fragment does not change approval policy.
Configure [the required native events](hooks.md#prepare-a-project) and review Hook trust in a new Codex session. Bind the session to its task claim.
Keep the server name `sdd_harness`. The native Hook matches that name for gate admission.
The status tools use standard MCP. The managed gate requires the Codex native events.

## Interpret the result

Use `reason_code` and `next_action` to branch on a `request_gate` answer. Keep the
human-readable `reason` when present. When the Hook denies before MCP runs, the
native denial starts with the same code and action in square brackets.

| Reason code | Next action |
| --- | --- |
| `gate_session_start_missing` | `reopen_trusted_session`: load the required Hook in a fresh trusted Codex session. |
| `gate_observation_missing_or_stale` | `restore_managed_gate_route`: check both required Hooks and MCP before retrying the same request. This code does not identify which component was missing. |
| `gate_evidence_stale` or `gate_manifest_changed` | `register_new_candidate`: keep the old record and follow the candidate procedure with current inputs. |
| `gate_policy_changed` | `review_policy_and_restart_server`: inspect the changed or unavailable policy, then restart the reviewed service. |
| `gate_outcome_unknown` or `gate_admission_busy` | `inspect_original_request`: inspect the original ID and its effects. An active admission ticket can exist before an operation is recorded. |
| `gate_registry_unavailable` | `inspect_original_request`: review the trusted registry so the original ID can be inspected. |
| `gate_request_not_recorded` | `inspect_original_request`: check the original invocation and possible effects. No record is not authority to retry. |
| `gate_replayed` | `read_existing_gate_result`: read the original operation and verdict. No new check ran. |
| `gate_passed` or `gate_failed` | Inspect selection prerequisites or review the failed gate, respectively. |

For a separately established retry of the same operation, keep the same request ID. Do not reuse it for another check or candidate.
A replay needs a fresh native call. It retrieves the same operation without running another gate if the evidence still applies.
A `denied` result refers to this invocation before handoff; it does not cancel an earlier recorded result with the same ID.
If a child response does not establish an admission or execution verdict, treat the original request as unknown.
For a `running`, `uncertain`, or `unknown` result, inspect the original request and its effects; do not retry automatically, replace its ID, or start a successor based on that result.
These states take precedence over stale evidence. Use the new candidate procedure only after the original outcome is understood and when the reason code calls for it.
A passing result shows one gate's decision. Use the existing CLI to check all selection prerequisites.
If MCP or a required Hook is unavailable, stop at acceptance. Keep the current evidence and restore the project setup. Direct CLI gate execution cannot substitute for this path.

Use the existing CLI to inspect the exact request without loading the MCP SDK:

```text
python -B <skill>/scripts/delivery.py --root <project> inspect --candidate <id> --gate <check> --request <request-id>
```

The CLI uses the bound registry. It does not admit or run a check, issue a
ticket, or write evidence. `recorded_status` is the stored verdict; `status`
can be `stale` when a recorded pass no longer applies or `historical` for a
matching completed operation on a retired or published candidate. When there is
no matching operation or active admission ticket, `gate_request_not_recorded`
comes before evidence checks. It does not prove which component failed,
that the current Codex session loaded a Hook, or that an external process stopped.
An exit code of zero means the inspection returned a result, not that the gate passed.
