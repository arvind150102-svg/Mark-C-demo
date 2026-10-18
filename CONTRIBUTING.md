# Contributions and community discussion

Use issues for questions about this example, reproducible arithmetic defects, documentation clarifications and non-confidential evaluation ideas. Include the commit, Python version, synthetic inputs, expected result and observed result when reporting a defect. Do not publish secrets, customer identities, financial statements or proprietary code.

Keep discussions respectful and on topic. No mass mentions, promotional link drops, unsolicited pitches or repeated contact after a decline. Project replies do not establish a consulting contract, paid pilot, deadline or data-sharing arrangement.

Before preparing a code contribution, discuss it with the owner: no open-source licence has been selected yet. Do not copy code from private repositories or submit material whose licensing is unclear. Disclose AI assistance where relevant and independently check mathematical claims.

Tests use only Python's standard library. Run python -m unittest discover -s tests -v and python pricing.py. Changes should preserve the distinction between assumed arithmetic and empirical evidence. Do not add telemetry, external services, dependencies or customer data without an explicit design review.

The HTML report must call the existing pricing and sensitivity functions; do not duplicate the arithmetic in a browser script. When changing its presentation, regenerate `examples/report.html` with `python report.py > examples/report.html`, review the diff, and open the report at narrow and wide viewport sizes. This explicit redirection replaces the generated fixture; the `--output` option intentionally refuses existing files. Keep exact inputs and results in the audit section, and keep the report usable offline. See [the quickstart](docs/QUICKSTART.md) for the reader's workflow.
