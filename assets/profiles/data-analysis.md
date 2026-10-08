# Data-Analysis Project Prompts

Use these prompts for a report, analysis, model, or repeatable data transformation.
For selection and composition, read [project profiles](../../references/project-profiles.md).
Fill relevant prompts in the existing record. Keep its format and authority.

## Specification prompts

- Identify permitted sources, source versions, access permissions, and coverage.
- Define data quality rules for missing values, duplicates, invalid values, and exclusions.
- Define observation grain, units, time basis, time zone, and relevant availability times.
- Define metric formulas, filtering, grouping, denominators, and rounding rules.
- State the analysis method, assumptions, uncertainty, and limitations.
- Supply independent expected examples with a source or calculation basis.
- Define reproducible execution inputs, code, dependencies, configuration, and output provenance.
- If prediction or backtesting applies, define time splits, leakage checks, and evaluation conditions.
- If a recurring pipeline applies, define retry, recovery, freshness, and delivery requirements.

Use authorized versions, hashes, or query definitions to identify sensitive inputs.
Do not require private or licensed raw datasets to enter Git.
If exact replay is restricted, state the restriction and its effect on validation.

## Acceptance example

Suppose the accepted metric is net revenue for completed orders in CNY during a stated reporting period.
Each input row represents one order. The accepted formula subtracts refunds from completed-order revenue.
The permitted sample has completed orders of 100 and 200, with respective refunds of 0 and 50.
A canceled order of 80 does not contribute.
The independent expected result is `100 + (200 - 50) = 250 CNY`.
The expected result comes from the accepted formula and sample, not the implementation's output.

The check also verifies the reporting period, source basis, and output provenance.
These example metric choices do not replace the project's accepted definitions.

## Conditional harness checks

- For calculated outputs, compare independent expected examples with actual results.
- Check applicable grain, units, time boundaries, filters, and data quality rules.
- For reproducible execution, rerun with identified inputs and compare accepted output properties.
- If numerical variation applies, check the accepted tolerance and stated uncertainty.
- If sources require restricted access, check authorized retrieval and declared replay limits.
- If prediction applies, check time splits and features available at the actual decision time.
- If backtesting applies, check execution assumptions and information availability before each simulated decision.
- If a pipeline applies, check relevant retry, recovery, freshness, and actual output delivery.

A successful run does not establish correct metric definitions or causal conclusions.
Record input provenance, query basis, candidate, execution conditions, actual outputs, and remaining limits in the existing evidence record.
