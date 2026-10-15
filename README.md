# Mark-C-demo
MARK C Demo illustrates a transparent SaaS pricing comparison using synthetic data, explicit assumptions and reproducible calculations. Explore two pricing options, inspect the arithmetic and review limitations. This educational example is separate from the private MARK C engine and does not establish real-world predictive accuracy.

# MARK C pricing example

Inspect the assumptions behind one SaaS pricing question: if a monthly price rises from $49 to $69, how many existing paying customers must remain to exceed the original monthly contribution?

MARK C is developing experimental, assumption-led decision support for founders and finance teams. This repository is an independently written educational example using synthetic inputs and exact arithmetic. It contains no proprietary engine code and does not run or validate the deployed MARK C application.

## Run locally

Use Python 3.10 or later. No third-party packages, API keys, database or network access are required by the example.

    python pricing.py
    python -m unittest discover -s tests -v
    python sensitivity.py

The script reads examples/pricing.json. Record your Python version and the repository commit when comparing results. Money inputs are finite nonnegative decimal strings; counts are nonnegative integers. The horizon must be exactly one month and amounts are labelled USD. Exact non-integer outputs are rational strings such as 3/5, avoiding hidden currency rounding.

The optional --input PATH argument reads a local synthetic JSON file. Input files are limited to 16 KiB; duplicate keys are rejected. Monetary strings are limited to 32 characters and customer counts to one billion. These are explicit resource limits, not economic constraints.

Run python sensitivity.py --retained 600 661 662 800 1000 for a deterministic table of assumed retention scenarios. No probabilities are calculated. See [the evaluation guide](docs/EVALUATION.md) for a practical review checklist.

## Read the arithmetic

All inputs are invented. Baseline: 1,000 customers paying $49 per month, with $10 variable cost per customer. Baseline contribution is (49 - 10) x 1,000 = $39,000. Alternative contribution is (69 - 10) x retained customers.

- 800 retained customers: $47,200 contribution, $8,200 above baseline.
- 600 retained customers: $35,400 contribution, $3,600 below baseline.
- 39,000 / 59 = 661.016949...; at least 662 whole paying customers exceed the baseline.

This compares contribution, not total profit. Fixed costs, tax, acquisition, expansion revenue, discounting, cohort timing and market response are excluded. Retention is an input assumption, not a forecast or measured price elasticity. A higher assumed contribution is not a recommendation to raise prices.

The threshold is reported only when the alternative unit contribution is positive and baseline contribution is nonnegative. Otherwise it is null rather than implying a general break-even solver. An attainable threshold is explicitly distinguished from one exceeding the baseline cohort.

## What has been checked

The test suite checks the arithmetic, threshold boundary, ties, zero counts and cost, scaled monetary inputs, input-key order, malformed inputs, unsupported horizons and exact fractional results. Tests validate this narrow example only. They do not establish real-world predictive accuracy, customer outcomes, business readiness, causal effects or production performance.

MARK C remains experimental and numerical validation continues. Operational use requires separate correction and revalidation. The broader economic model is a development vision. No AI learning or web retrieval is performed by this example, and no claim of improved mathematical or economic modelling follows from it.

GitHub Actions runs these same tests and fixture comparisons on pushes and pull requests. The workflow has read-only repository permissions, no secret references, no dependency installation and a five-minute timeout. A green run validates only this example.

## Discuss a bounded evaluation

If your team is considering a similar decision, contact Arvind at arvind150102@gmail.com with the decision type and the baseline method you currently use. Please do not send confidential financial records, personal customer data or credentials.

We can discuss evaluation scope and success criteria. Any paid pilot, fee, timing, data access or other commitment requires separate agreement. Existing free-beta commitments remain unchanged. This is an invitation to an optional conversation, not an offer of guaranteed returns or deployment readiness.

## Contributing and permissions

Read CONTRIBUTING.md before submitting an issue or contribution. A helpful reproduction, mathematical correction or documentation clarification is welcome. Do not use issues for unsolicited advertising or confidential information.

No open-source licence has been selected. Public visibility is not a grant of an additional software licence. Please contact the owner before redistribution or reuse requiring permission. Nothing here changes ownership or permissions for the private MARK C engine.
