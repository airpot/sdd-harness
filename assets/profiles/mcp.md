# MCP Project Prompts

Use these prompts for an MCP server or an MCP capability that it supplies.
For selection and composition, read [project profiles](../../references/project-profiles.md).
Write information for the related prompts in the record that the project uses.
Keep its format and authority.

## Specification prompts

For the related prompts, use these instructions:

- Identify the selected protocol version, SDK version, and supported client.
- Identify the transport and deployment environment that the server uses.
- Give the capabilities that the server supplies. For example, give tools, resources, or prompts.
- Give input schemas, output schemas, validation rules, and error behavior.
- Give initialization, capability negotiation, and compatibility requirements.
- For writes, give side effects and necessary authorization.
- For completion with an unknown outcome, give status inspection, request identity, and permitted retry behavior.
- If network authentication is necessary for the transport, give its applicable identity and access rules.

Select only capabilities that the deliverable supplies.

A network transport that the local stdio server does not use is not necessary.
An authentication system that the server does not use is also not necessary.

Do not add a hosted service only to give information for these prompts.

## Acceptance example

For this example, the accepted reservation contract uses `reservation_key` as the application request identity.
This identity is different from a protocol message ID.
A client sends `reservation_key=R17` for one seat.
The server makes the reservation, but the client does not get the response.

The client uses outcome inspection that the interface supplies or does a retry with `R17`.
For this retry, the client uses applicable replay protection that the checks show.
The expected result gives the same reservation without a second seat deduction.
Changed inputs for `R17` give the specified conflict result from the contract.

If a retry mechanism has no project acceptance or satisfactory checks, this example does not make the mechanism necessary.

Obey [the recovery rule](../../references/workflow.md#resolve-uncertain-effects).
If aggregate inventory cannot identify R17 and there is no request-status interface, keep the inspection limitation.
If the project supplies no basis for an inspection interface, do not use the interface.

With replay authorization, you can use the same target, key, and inputs in the scope that the evidence shows.

Use this permission only in the retention period and retry limits that the evidence shows.
Until applicable result evidence shows the outcome, keep the outcome status unknown.

## Conditional harness checks

For applicable checks, use these instructions:

- For each capability that the server supplies, use the supported client in operation through the selected transport.
- Compare initialization and negotiated capabilities with the accepted compatibility contract.
- Do checks of correct inputs, incorrect inputs, output schemas, and observable error behavior.
- If a capability writes state, examine the state after the write and the authorization boundary.
- If retries are applicable, make a response loss occur. Then, do a check of behavior for the accepted request identity.
- If cancellation has an effect for completion, examine the state after cancellation and the completion status in the report.
- If network authentication is applicable, do checks of accepted and rejected access through the transport that the server uses.
- If client or SDK versions change, do a check of the compatibility boundary for this change.

A correct schema does not show compatibility with the supported client in operation or correct side effects.
Mocks can show behavior in isolated components.
But mocks cannot replace the necessary check with the supported client in operation.

In the evidence record that the project uses, record:
- The protocol
- The SDK
- The client
- The transport
- The candidate
- Execution results
- Checks that you cannot do.
