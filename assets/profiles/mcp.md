# MCP Project Prompts

Use these prompts for an MCP server or exposed MCP capability.
For selection and composition, read [project profiles](../../references/project-profiles.md).
Fill relevant prompts in the existing record. Keep its format and authority.

## Specification prompts

- Identify the selected protocol version, SDK version, and supported client.
- Identify the actual transport and deployment environment.
- Define exposed capabilities, such as tools, resources, or prompts.
- Define input schemas, output schemas, validation rules, and error behavior.
- State initialization, capability negotiation, and compatibility requirements.
- For writes, define actual side effects and required authorization.
- For uncertain completion, define status inspection, request identity, and permitted retry behavior.
- If the actual transport requires network authentication, define its applicable identity and access rules.

Select only capabilities that the deliverable exposes.
A local stdio server does not require an unused network transport or authentication system.
Do not add a hosted service merely to satisfy these prompts.

## Acceptance example

Suppose an accepted reservation contract uses an application request identity, `reservation_key`.
This identity differs from a protocol message ID.
A client submits `reservation_key=R17` for one seat.
The server creates the reservation, but the client loses the response.
The client checks actual state or retries with `R17` under the accepted contract.
The expected result returns the same reservation without another seat deduction.
Changed inputs for `R17` produce the contract's defined conflict result.

This example requires no retry mechanism that the project has not accepted.
After uncertain effects, inspect actual state before repeating a write.

## Conditional harness checks

- For exposed capabilities, use the supported real client through the selected transport.
- Check initialization and negotiated capabilities against the accepted compatibility contract.
- Check valid inputs, invalid inputs, output schemas, and observable error behavior.
- If a capability writes state, inspect the actual changed state and authorization boundary.
- If retries apply, reproduce a lost response and check the accepted request identity behavior.
- If cancellation affects completion, check the resulting state and reported completion status.
- If network authentication applies, check accepted and rejected access through the actual transport.
- If client or SDK versions change, check the affected compatibility boundary.

Schema validity does not establish real-client compatibility or correct side effects.
Mocks can check isolated behavior but do not replace the necessary real-client check.
Record protocol, SDK, client, transport, candidate, actual results, and unavailable checks in the existing evidence record.
