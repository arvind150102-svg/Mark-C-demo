"""Export an offline HTML report of the public synthetic pricing example."""
import argparse
from fractions import Fraction
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import sys

from pricing import compare, load_inputs
from sensitivity import sensitivity


def amount(value):
    """Format exact terminating fractions as USD without float rounding."""
    value = Fraction(value)
    denominator = value.denominator
    twos = fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        return f'USD {value}'
    places = max(twos, fives)
    scale = 10 ** places
    units = abs(value.numerator) * scale // value.denominator
    whole, tail = divmod(units, scale)
    decimals = ('.' + str(tail).zfill(places).rstrip('0')) if tail else ''
    return f'{"-" if value < 0 else ""}${whole:,}{decimals}'


def default_counts(data, result):
    """Choose feasible examples, including both sides of the strict threshold."""
    cohort = data['baseline_customers']
    counts = {0, cohort, cohort * 3 // 5, data['retained_customers']}
    threshold = result['minimum_customers_to_exceed_baseline']
    if threshold is not None:
        counts.update(n for n in (threshold - 1, threshold) if 0 <= n <= cohort)
    return sorted(counts)


def render_report(data, retained_counts=None):
    """Render validated assumptions through the existing calculation functions."""
    result = compare(data)
    counts = default_counts(data, result) if retained_counts is None else retained_counts
    scenarios = sensitivity(data, counts)
    normalized = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')
    digest = sha256(normalized).hexdigest()
    threshold = result['minimum_customers_to_exceed_baseline']
    if threshold is None:
        threshold_text = ('Not calculated: this example requires positive alternative '
                          'unit contribution and nonnegative baseline contribution. '
                          'Use the scenario table to inspect the assumed outcomes.')
    elif result['threshold_within_baseline_cohort']:
        threshold_text = (f'{threshold:,} retained customers are needed to strictly exceed '
                          'the baseline. A tie does not exceed it.')
    else:
        threshold_text = (f'{threshold:,} customers would be required, exceeding the '
                          f'{data["baseline_customers"]:,}-customer starting cohort. '
                          'This threshold is unattainable under the retention-only assumption.')
    labels = {'tie': 'Equal contribution', 'alternative_higher': 'Alternative higher',
              'baseline_higher': 'Baseline higher'}
    fields = [('Baseline monthly price', amount(data['baseline_price'])),
              ('Alternative monthly price', amount(data['alternative_price'])),
              ('Variable cost per customer / month', amount(data['unit_cost'])),
              ('Starting paying customers', f'{data["baseline_customers"]:,}'),
              ('Selected retained customers', f'{data["retained_customers"]:,}'),
              ('Comparison period / currency', '1 month / USD')]
    assumptions = ''.join(f'<tr><th scope="row">{escape(k)}</th><td>{escape(v)}</td></tr>'
                          for k, v in fields)
    rows = []
    for row in scenarios['rows']:
        selected = row['retained_customers'] == data['retained_customers']
        marker = ' <span class="tag">Selected</span>' if selected else ''
        rows.append(f'<tr class="{"selected" if selected else "scenario"}">'
                    f'<th scope="row">{row["retained_customers"]:,}{marker}</th>'
                    f'<td>{escape(amount(row["alternative_contribution"]))}</td>'
                    f'<td>{escape(amount(row["difference"]))}</td>'
                    f'<td>{labels[row["comparison"]]}</td></tr>')
    audit = json.dumps({'report_format_version': 1, 'input_sha256': digest,
                       'inputs': data, 'comparison': result, 'scenarios': scenarios},
                      indent=2, sort_keys=True)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>MARK C | Pricing assumption report</title>
<style>
:root {{ color-scheme: light; font-family: system-ui, sans-serif; color: #17243b; background: #edf1f7; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; line-height: 1.6; }}
main {{ max-width: 1020px; margin: 32px auto; padding: 36px; background: #fff; border-radius: 18px; }}
header {{ border-bottom: 1px solid #dbe1eb; padding-bottom: 22px; }}
.eyebrow {{ color: #4c4288; font-weight: 750; letter-spacing: .12em; font-size: .8rem; }}
h1 {{ margin: 8px 0; font-size: clamp(1.8rem, 5vw, 2.6rem); line-height: 1.15; }}
h2 {{ font-size: 1.2rem; margin-top: 30px; }}
p {{ margin: 10px 0; }}
.lede {{ max-width: 75ch; color: #45536a; }}
.notice {{ padding: 14px 18px; border-left: 4px solid #6554a4; background: #f2f0fa; }}
.cards {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin: 24px 0; }}
.card {{ background: #f3f6fa; border: 1px solid #dbe1eb; border-radius: 12px; padding: 18px; }}
.card p {{ margin: 0; color: #45536a; font-size: .9rem; }}
.value {{ display: block; margin: 8px 0; font-size: clamp(1.3rem, 4vw, 1.8rem); font-weight: 750; overflow-wrap: anywhere; }}
.card small {{ color: #45536a; }}
table {{ width: 100%; border-collapse: collapse; font-size: .95rem; }}
caption {{ text-align: left; color: #45536a; padding-bottom: 10px; }}
th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #dbe1eb; overflow-wrap: anywhere; }}
thead {{ background: #17243b; color: #fff; }}
tbody th {{ font-weight: 550; }}
.selected {{ background: #eef5f2; }}
.tag {{ font-size: .75rem; font-weight: 650; color: #215d46; display: inline-block; }}
.threshold {{ padding: 16px 20px; border: 1px solid #c9d3e4; border-radius: 10px; }}
.math, code {{ font-family: ui-monospace, monospace; overflow-wrap: anywhere; }}
pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #f3f6fa; padding: 16px; font-size: .8rem; }}
summary {{ cursor: pointer; padding: 10px 0; font-weight: 650; }}
footer {{ color: #45536a; font-size: .85rem; border-top: 1px solid #dbe1eb; margin-top: 28px; padding-top: 16px; }}
@media (max-width: 640px) {{ main {{ margin: 0; padding: 20px; border-radius: 0; }} .cards {{ grid-template-columns: 1fr; gap: 10px; }} th, td {{ padding: 8px 4px; font-size: .8rem; }} .value {{ margin: 4px 0; }} }}
@media print {{ :root {{ background: #fff; }} main {{ margin: 0; padding: 0; }} .cards, tr, .threshold {{ break-inside: avoid; }} .audit {{ display: none; }} }}
</style>
</head>
<body><main>
<header><div class="eyebrow">MARK C / PUBLIC PRICING EXAMPLE</div>
<h1>What must remain after a price change?</h1>
<p class="lede">Compare two monthly prices against an explicit retained-customer assumption.
Every result below follows from the stated inputs.</p>
<p class="notice"><strong>Synthetic evaluation only.</strong> Retention is an assumption;
this report assigns no likelihood to it and makes no price recommendation.</p></header>
<section aria-label="Selected scenario results" class="cards">
<div class="card"><p>Baseline contribution</p><span class="value">{escape(amount(result['baseline_contribution']))}</span><small>{data['baseline_customers']:,} starting customers</small></div>
<div class="card"><p>Alternative contribution</p><span class="value">{escape(amount(result['alternative_contribution']))}</span><small>{data['retained_customers']:,} assumed retained customers</small></div>
<div class="card"><p>Difference from baseline</p><span class="value">{escape(amount(result['difference']))}</span><small>{labels[result['comparison']]}</small></div>
</section>
<section><h2>01 / Inspect the assumptions</h2>
<table><caption>Invented inputs; all monetary amounts are USD.</caption><tbody>{assumptions}</tbody></table>
<p class="math">Baseline: ({escape(amount(data['baseline_price']))} − {escape(amount(data['unit_cost']))}) × {data['baseline_customers']:,} = {escape(amount(result['baseline_contribution']))}<br>
Alternative: ({escape(amount(data['alternative_price']))} − {escape(amount(data['unit_cost']))}) × {data['retained_customers']:,} = {escape(amount(result['alternative_contribution']))}</p></section>
<section><h2>02 / Check the retention boundary</h2>
<p class="threshold">{escape(threshold_text)}</p>
<table><caption>Assumed retention scenarios, sorted by customer count. Rows are not forecasts.</caption>
<thead><tr><th scope="col">Retained customers</th><th scope="col">Alternative contribution</th><th scope="col">Difference</th><th scope="col">Comparison</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<p>Money is displayed exactly, without rounding to cents. The audit data retains the calculator's rational strings.</p></section>
<section><h2>03 / Decide what to validate next</h2>
<p>Compare one pricing question with your existing spreadsheet baseline. Agree how to assess
calculation consistency, assumption clarity and review effort before discussing a fixed-fee pilot.</p>
<p>Contribution excludes fixed costs, tax, acquisition, expansion, discounting and market response.
Evidence about actual retention must come from a separate evaluation. This educational example
does not run or validate the private MARK C engine or establish production readiness.</p>
<p>For an evaluation discussion: arvind150102@gmail.com. Use synthetic or nonconfidential inputs.
Scope, fee, timing and data access require separate agreement; licensing or technology transfer
would be scoped separately after evaluation.</p></section>
<section class="audit"><h2>Reproduce this report</h2>
<p>Generated by <code>report.py</code> using <code>pricing.compare</code> and
<code>sensitivity.sensitivity</code>. Report format 1. Record the repository commit and Python
version separately when comparing reports.</p>
<details><summary>Exact inputs, results and input fingerprint</summary><pre>{escape(audit)}</pre></details>
<p>The SHA-256 fingerprint covers normalized inputs only; it is not evidence of validation or authorship.</p></section>
<footer>MARK C remains experimental. This static file works offline, with no scripts, telemetry or external assets.
Use your browser's print command for a printable summary.</footer>
</main></body></html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path(__file__).parent/'examples'/'pricing.json')
    parser.add_argument('--retained', type=int, nargs='+', help='1–101 unique retained-customer counts')
    parser.add_argument('--output', type=Path, help='Create a new HTML file; omit to write to stdout')
    args = parser.parse_args()
    try:
        document = render_report(load_inputs(args.input), args.retained)
        if args.output:
            # Exclusive creation prevents replacing an input file or an earlier report.
            with args.output.open('x', encoding='utf-8', newline='\n') as stream:
                stream.write(document)
        else:
            sys.stdout.buffer.write(document.encode('utf-8'))
    except (ValueError, OSError) as exc:
        parser.exit(2, f'Cannot create report: {exc}\n')


if __name__ == '__main__':
    main()
