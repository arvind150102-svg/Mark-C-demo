import json
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from pricing import compare, load_inputs
from sensitivity import sensitivity

ROOT=Path(__file__).resolve().parents[1]

class ExtendedTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'examples/pricing.json').read_text())
    def test_exhaustive_integer_reference(self):
        # Independent integer arithmetic and exhaustive feasible-count search.
        for p0 in range(4):
            for p1 in range(4):
                for cost in range(4):
                    for base_n in range(7):
                        for retained in range(base_n+1):
                            d=dict(self.data,baseline_price=str(p0),alternative_price=str(p1),unit_cost=str(cost),baseline_customers=base_n,retained_customers=retained)
                            r=compare(d)
                            base=(p0-cost)*base_n;alt=(p1-cost)*retained
                            self.assertEqual(Fraction(r['baseline_contribution']),base)
                            self.assertEqual(Fraction(r['alternative_contribution']),alt)
                            self.assertEqual(Fraction(r['difference']),alt-base)
                            if p1>cost and base>=0:
                                threshold=base//(p1-cost)+1
                                self.assertEqual(r['minimum_customers_to_exceed_baseline'],threshold)
                                feasible=[n for n in range(base_n+1) if (p1-cost)*n>base]
                                self.assertEqual(r['threshold_within_baseline_cohort'],bool(feasible))
                                if feasible:self.assertEqual(min(feasible),threshold)
                            else:self.assertIsNone(r['minimum_customers_to_exceed_baseline'])
    def test_sensitivity_fixture(self):
        expected=json.loads((ROOT/'examples/sensitivity_expected.json').read_text())
        self.assertEqual(sensitivity(self.data,[600,661,662,800,1000]),expected)
    def test_sensitivity_order_invariance(self):
        self.assertEqual(sensitivity(self.data,[800,600]),sensitivity(self.data,[600,800]))
    def test_positive_margin_monotonicity(self):
        rows=sensitivity(self.data,list(range(0,1001,10)))['rows']
        values=[Fraction(r['alternative_contribution']) for r in rows]
        self.assertEqual(values,sorted(values))
    def test_negative_margin_monotonicity(self):
        rows=sensitivity(dict(self.data,alternative_price='5'),[0,100,200])['rows']
        self.assertEqual([r['alternative_contribution'] for r in rows],['0','-500','-1000'])
    def test_sensitivity_validation(self):
        for bad in [[],[1,1],[True],[1.0],[-1],[1001],list(range(102)),(1,2)]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):sensitivity(self.data,bad)
    def test_resource_limits(self):
        for field,value in [('baseline_price','9'*33),('baseline_customers',1000000001)]:
            with self.subTest(field=field),self.assertRaises(ValueError):compare(dict(self.data,**{field:value}))
    def test_json_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'input.json';p.write_text('{"currency":"USD","currency":"INR"}')
            with self.assertRaisesRegex(ValueError,'Duplicate'):load_inputs(p)
    def test_invalid_json_files(self):
        for raw in [b'x'*16385,b'\xff',b'null',b'[]',b'{',b'['*2000+b']'*2000]:
            with tempfile.TemporaryDirectory() as td:
                p=Path(td)/'input.json';p.write_bytes(raw)
                with self.assertRaises(ValueError):load_inputs(p)
    def test_cli_valid(self):
        for script in ['pricing.py','sensitivity.py']:
            with tempfile.TemporaryDirectory() as working_directory:
                p=subprocess.run([sys.executable,str(ROOT/script)],capture_output=True,text=True,check=True,cwd=working_directory)
            self.assertIsInstance(json.loads(p.stdout),dict)
            self.assertEqual(p.stderr,'')
    def test_cli_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'input.json';p.write_text('{"bad":1}')
            for script in ['pricing.py','sensitivity.py']:
                result=subprocess.run([sys.executable,str(ROOT/script),'--input',str(p)],capture_output=True,text=True)
                self.assertEqual(result.returncode,2)
                self.assertEqual(result.stdout,'')
                self.assertNotIn('Traceback',result.stderr)
    def test_zero_margin(self):
        self.assertIsNone(compare(dict(self.data,alternative_price='10'))['minimum_customers_to_exceed_baseline'])
    def test_unattainable_threshold(self):
        r=compare(dict(self.data,alternative_price='11'))
        self.assertEqual(r['minimum_customers_to_exceed_baseline'],39001)
        self.assertFalse(r['threshold_within_baseline_cohort'])
    def test_currency_scale_fraction(self):
        original=compare(self.data)
        scaled=compare(dict(self.data,baseline_price='4.9',alternative_price='6.9',unit_cost='1'))
        self.assertEqual(Fraction(scaled['difference'])*10,Fraction(original['difference']))
        self.assertEqual(scaled['minimum_customers_to_exceed_baseline'],original['minimum_customers_to_exceed_baseline'])

if __name__=='__main__':unittest.main()
