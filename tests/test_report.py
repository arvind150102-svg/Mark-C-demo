from fractions import Fraction
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from pricing import compare
from report import amount, render_report

ROOT = Path(__file__).resolve().parents[1]


class ReportParser(HTMLParser):
    def __init__(self, document):
        super().__init__()
        self.in_pre = False
        self.audit = ''
        self.tags = []
        self.attrs = []
        self.feed(document)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.extend(attrs)
        if tag == 'pre':
            self.in_pre = True

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.in_pre = False

    def handle_data(self, data):
        if self.in_pre:
            self.audit += data


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT/'examples/pricing.json').read_text())

    def test_display_and_audit_agree_with_calculation(self):
        document = render_report(self.data)
        self.assertIn('$39,000', document)
        self.assertIn('$47,200', document)
        self.assertIn('$8,200', document)
        audit = json.loads(ReportParser(document).audit)
        self.assertEqual(audit['inputs'], self.data)
        self.assertEqual(audit['comparison'], compare(self.data))
        canonical = json.dumps(self.data, sort_keys=True, separators=(',', ':')).encode()
        self.assertEqual(audit['input_sha256'], sha256(canonical).hexdigest())
        for row in audit['scenarios']['rows']:
            count = row['retained_customers']
            self.assertEqual({k: v for k, v in row.items() if k != 'retained_customers'},
                             compare(dict(self.data, retained_customers=count)))

    def test_default_scenarios_include_strict_boundary(self):
        rows = json.loads(ReportParser(render_report(self.data)).audit)['scenarios']['rows']
        indexed = {r['retained_customers']: r for r in rows}
        self.assertEqual(indexed[661]['difference'], '-1')
        self.assertEqual(indexed[662]['difference'], '58')
        self.assertIn('662 retained customers', render_report(self.data))

    def test_threshold_at_tie_requires_one_more_customer(self):
        data = dict(self.data, alternative_price='49', retained_customers=1000)
        document = render_report(data)
        self.assertIn('Equal contribution', document)
        self.assertIn('1,001 customers would be required', document)
        self.assertIn('unattainable', document)

    def test_zero_cohort_has_one_feasible_scenario(self):
        document = render_report(dict(self.data, baseline_customers=0, retained_customers=0))
        audit = json.loads(ReportParser(document).audit)
        self.assertEqual(audit['scenarios']['scenario_count'], 1)
        self.assertEqual(audit['scenarios']['rows'][0]['retained_customers'], 0)
        self.assertIn('unattainable', document)

    def test_negative_margin_and_baseline_do_not_claim_no_solution(self):
        for changes in [{'alternative_price': '5'}, {'baseline_price': '5'}]:
            with self.subTest(changes=changes):
                document = render_report(dict(self.data, **changes))
                self.assertIn('Not calculated:', document)
                self.assertNotIn('unattainable', document)

    def test_small_cohort_defaults_and_custom_scenarios(self):
        data = dict(self.data, baseline_customers=3, retained_customers=2)
        for counts in [None, [3, 0, 2]]:
            rows = json.loads(ReportParser(render_report(data, counts)).audit)['scenarios']['rows']
            self.assertTrue(all(0 <= r['retained_customers'] <= 3 for r in rows))
        rows = json.loads(ReportParser(render_report(data, [3, 0, 2])).audit)['scenarios']['rows']
        self.assertEqual([r['retained_customers'] for r in rows], [0, 2, 3])

    def test_preserves_subcent_amounts_without_float_rounding(self):
        self.assertEqual(amount('3/5'), '$0.6')
        self.assertEqual(amount('-3/5000'), '-$0.0006')
        self.assertEqual(amount('1/3'), 'USD 1/3')
        # Maximum supported monetary precision must survive report presentation.
        value = '0.' + '0' * 29 + '1'
        self.assertEqual(Fraction(amount(value).replace('$', '').replace(',', '')), Fraction(value))
        data = dict(self.data, baseline_price='0.3', alternative_price='0.4',
                    unit_cost='0.1', baseline_customers=3, retained_customers=2)
        document = render_report(data)
        self.assertIn('$0.6', document)
        self.assertIn('Equal contribution', document)
        self.assertEqual(json.loads(ReportParser(document).audit)['comparison']['difference'], '0')

    def test_report_is_deterministic_and_does_not_mutate_inputs(self):
        before = dict(self.data)
        first = render_report(self.data, [800, 600])
        second = render_report(dict(reversed(list(self.data.items()))), [600, 800])
        self.assertEqual(first, second)
        self.assertEqual(self.data, before)

    def test_report_has_no_active_content_or_external_resources(self):
        parsed = ReportParser(render_report(self.data))
        self.assertTrue({'html', 'title', 'main', 'caption', 'thead', 'th'}.issubset(parsed.tags))
        self.assertFalse({'script', 'iframe', 'img', 'link', 'form', 'object', 'embed'} & set(parsed.tags))
        self.assertFalse(any(k in ('src', 'href') or k.startswith('on') for k, v in parsed.attrs))
        self.assertIn(('lang', 'en'), parsed.attrs)
        self.assertIn(('http-equiv', 'Content-Security-Policy'), parsed.attrs)

    def test_invalid_inputs_and_counts_rejected(self):
        with self.assertRaises(ValueError):
            render_report(dict(self.data, baseline_price='<script>alert(1)</script>'))
        for counts in [[], [800, 800], [True], [1001], list(range(102))]:
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                render_report(self.data, counts)

    def test_cli_writes_utf8_from_other_directory(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td)/'report.html'
            result = subprocess.run([sys.executable, str(ROOT/'report.py'), '--output', str(output)],
                                    cwd=td, capture_output=True, check=True)
            self.assertEqual(output.read_text(encoding='utf-8'), render_report(self.data))
            self.assertEqual(result.stdout, b'')
            self.assertEqual(result.stderr, b'')
            stdout = subprocess.run([sys.executable, str(ROOT/'report.py')], cwd=td,
                                    capture_output=True, check=True).stdout
            self.assertEqual(stdout, output.read_bytes())

    def test_cli_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td)/'existing.html'
            output.write_text('Keep this content', encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT/'report.py'), '--output', str(output)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('Traceback', result.stderr)
            self.assertEqual(output.read_text(), 'Keep this content')

    def test_cli_invalid_scenario_creates_no_file(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td)/'report.html'
            result = subprocess.run([sys.executable, str(ROOT/'report.py'), '--retained', '1001',
                                     '--output', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(output.exists())
            self.assertEqual(result.stdout, '')
            self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
