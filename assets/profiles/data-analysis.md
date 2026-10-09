# Data-Analysis Project Prompts

Use these prompts for a report, analysis, model, or data transformation that you can do again.
For selection and composition, read [project profiles](../../references/project-profiles.md).
Write information for the related prompts in the record that the project uses.
Keep its format and authority.

## Specification prompts

For the related prompts, use these instructions:

- Identify permitted sources, source versions, access permissions, and coverage.
- Give data quality rules for missing values, duplicates, invalid values, and exclusions.
- Give observation grain, units, time basis, time zone, and related availability times.
- Give metric formulas, filtering, grouping, denominators, and rounding rules.
- Give the analysis method, assumptions, uncertainty, and limitations.
- Supply expected examples from a source or calculation that does not use the implementation output.
- Give the inputs, code, dependencies, configuration, and output provenance that let you do the same execution again.
- If prediction or backtesting is applicable, give time splits, leakage checks, and evaluation conditions.
- If a pipeline operates again and again, give retry, recovery, freshness, and delivery requirements.

Use permitted versions, hashes, or query definitions to identify sensitive inputs.
Do not make Git storage necessary for raw datasets with privacy conditions or license conditions.
If the same execution has replay restrictions, give these restrictions and their effect for validation.

## Acceptance example

This example uses an accepted metric of net revenue for completed orders in CNY during a specified reporting period.
Each input row has data for one order.
The accepted formula subtracts refunds from revenue for completed orders.
The permitted sample has a completed order of 100 with a refund of 0.
It also has a completed order of 200 with a refund of 50.
The formula does not include a canceled order of 80.

For this example, the calculation independently gives `100 + (200 - 50) = 250 CNY`.
The accepted formula and sample give this expected result.
The implementation output is not the basis for this result.
The check also makes sure that the reporting period, source basis, and output provenance are correct.
These example metric selections do not replace the accepted definitions from the project.

## Conditional harness checks

For applicable checks, use these instructions:

- For calculated outputs, compare expected examples that use no implementation output with the execution results.
- Do checks of applicable grain, units, time boundaries, filters, and data quality rules.
- For replay, do the execution again with the identified inputs.
  Then, compare the results with the accepted output properties.
- If numerical variation is applicable, do a check of the accepted tolerance and specified uncertainty.
- If sources have access restrictions, do checks of permitted retrieval and the specified replay limits.
- If prediction is applicable, examine time splits and features available at each decision time.
- For backtesting, before each decision in the simulation, examine execution assumptions and information availability.
- If a pipeline is applicable, examine related retry, recovery, freshness, and output delivery from execution.

Execution with satisfactory results does not show correct metric definitions or correct conclusions about causes.

In the evidence record that the project uses, record:
- Input provenance
- The query basis
- The candidate
- Execution conditions
- Execution outputs
- Remaining limits.
