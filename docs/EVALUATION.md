# Evaluate a pricing question safely

This public example helps discuss an assumption-led pricing calculation. It does not run the MARK C engine, learn demand, forecast retention or recommend a commercial decision.

## Start with one decision

Describe the current monthly price, proposed price, variable servicing cost and existing paying cohort. Keep the example in USD over exactly one month. Use invented or public aggregate numbers in public issues; do not upload confidential business data.

Write down the baseline method you use today. Agree what should be compared: arithmetic agreement, ability to inspect assumptions, handling of invalid inputs and clarity of limitations. A clean test result is evidence of this example's calculation behaviour, not evidence of business impact.

## Reproduce the baseline

Run python pricing.py and python -m unittest discover -s tests -v. Record the commit and Python version. Compare the output with examples/expected.json. Run python sensitivity.py to compare five assumed retention counts against the same baseline; its expected output is in examples/sensitivity_expected.json.

Change only one assumption at a time in a local copy of examples/pricing.json, then use --input followed by that path. The sensitivity command also accepts --retained followed by integer counts. It sorts the rows, rejects duplicates and accepts at most 101 scenarios. Scenario frequency is never a probability or robustness score.

## Interpret the limits

Contribution means price minus variable cost, multiplied by paying customers. It excludes fixed costs, taxes, acquisition, timing and other cash flows. Higher contribution at an assumed retained count says nothing about whether that count is likely. Retention must be estimated independently before a real pricing decision.

The strict threshold is the smallest whole customer count that exceeds baseline contribution. It is only calculated for a positive alternative margin and a nonnegative baseline contribution. A threshold outside the original cohort is labelled unattainable under the retention-only assumption. Ties are reported as ties.

## Discuss an evaluation

A useful enquiry states the decision, the baseline method, the non-confidential evaluation criteria and the limitations that matter to your team. Send it to arvind150102@gmail.com or use the welcome issue for public, non-confidential questions. Do not send credentials, customer records or financial statements.

Any paid pilot, fee, delivery date, confidential-data access or contract needs separate agreement. Existing free-beta commitments remain unchanged. MARK C remains experimental; operational use requires separate correction and revalidation. This example cannot establish deployment readiness, predictive accuracy or guaranteed returns.
