# Review the pricing example in five minutes

## Open a report without installing Python

Download `examples/report.html` from this repository (use **Download raw file** on its GitHub file page), then open it in your browser. It is a static, self-contained report: it works offline and does not send inputs anywhere. GitHub's file view shows the HTML source rather than the rendered report. Browser print can produce a PDF summary; expand the audit section on screen to inspect the machine-readable results.

The committed report uses invented inputs only. It is an example of the public calculator, separate from the private MARK C engine.

## Read the example

1. Inspect the baseline: 1,000 customers at $49/month, with $10 variable cost each. Monthly contribution is $39,000.
2. Inspect the alternative: $69/month and 800 assumed retained customers produce $47,200, a difference of $8,200.
3. Look at the boundary: 661 retained customers produce $38,999, while 662 produce $39,058. The alternative first exceeds the baseline at 662 customers.
4. Challenge the retention assumption. The report does not say whether retaining 662 or 800 customers is likely.

Contribution is not total profit. Fixed costs, taxes, acquisition, expansion, discounting and market response are outside this example.

## Make a local report from synthetic inputs

Download or clone the repository. In its directory, use Python 3.10 or later:

```bash
python report.py --output my-pricing-report.html
python -m unittest discover -s tests -v
```

Open `my-pricing-report.html` in your browser. Output files must be new: the command refuses to overwrite existing files. To regenerate a report, choose a new filename. No dependencies or accounts are needed.

Edit a local copy of `examples/pricing.json` with invented inputs, keeping all seven fields. Money remains a decimal string, counts remain integers, currency remains USD and the period remains one month:

```bash
python report.py --input my-scenario.json --retained 600 661 662 800 1000 --output my-scenario-report.html
```

Counts must be unique, between zero and the starting cohort, with no more than 101 scenarios. Without `--retained`, the report includes the selected count, zero, 60% of the cohort, the whole cohort, and the two strict-threshold boundary counts when feasible. Duplicate counts are collapsed for these generated defaults. The 60% row is an illustrative assumption, not an estimated likelihood. When supplying `--retained`, the summary still uses `retained_customers` from the input; the table shows exactly the requested counts.

For JSON outputs, `python pricing.py` and `python sensitivity.py` continue to work unchanged. The HTML audit section contains the exact inputs, comparison and scenario rows. Money displays without cent rounding; original rational strings remain in the audit. The input fingerprint covers normalized JSON only. Record `python --version` and `git rev-parse HEAD` alongside any report used for comparison; the fingerprint does not identify the code version.

## Prepare a useful evaluation question

Use [the evaluation guide](EVALUATION.md) to record one use case, your current spreadsheet baseline and agreed validation criteria. A useful question is: “Can we reproduce this calculation, expose its assumptions and explain the differences from our baseline?” Any paid pilot requires separately agreed scope, fee and timing; licensing or technology transfer follows a separate discussion.

Questions and corrections can go in a repository issue with the commit, Python version, synthetic input and expected versus observed result. See [CONTRIBUTING.md](../CONTRIBUTING.md). Keep customer data and confidential records out of public issues.
