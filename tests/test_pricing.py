import json
from pathlib import Path
import unittest
from pricing import compare

class PricingTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((Path(__file__).resolve().parents[1]/'examples'/'pricing.json').read_text())
    def test_expected_fixture(self):
        expected=json.loads((Path(__file__).resolve().parents[1]/'examples'/'expected.json').read_text())
        self.assertEqual(compare(self.data),expected)
    def test_reference(self):
        r=compare(self.data)
        self.assertEqual((r['baseline_contribution'],r['alternative_contribution'],r['difference']),('39000','47200','8200'))
        self.assertEqual(r['minimum_customers_to_exceed_baseline'],662)
    def test_low_retention(self):
        self.data['retained_customers']=600
        self.assertEqual(compare(self.data)['alternative_contribution'],'35400')
        self.assertEqual(compare(self.data)['comparison'],'baseline_higher')
    def test_boundary(self):
        self.data['retained_customers']=661
        self.assertEqual(compare(self.data)['comparison'],'baseline_higher')
        self.data['retained_customers']=662
        self.assertEqual(compare(self.data)['comparison'],'alternative_higher')
    def test_tie(self):
        self.data.update(alternative_price='49',retained_customers=1000)
        self.assertEqual(compare(self.data)['comparison'],'tie')
    def test_zero(self):
        self.data.update(baseline_customers=0,retained_customers=0)
        self.assertEqual(compare(self.data)['comparison'],'tie')
    def test_zero_cost(self):
        self.data['unit_cost']='0'
        self.assertEqual(compare(self.data)['baseline_contribution'],'49000')
    def test_currency_scale(self):
        for key in ['baseline_price','alternative_price','unit_cost']:self.data[key]=str(int(self.data[key])*100)
        self.assertEqual(compare(self.data)['minimum_customers_to_exceed_baseline'],662)
        self.assertEqual(compare(self.data)['difference'],'820000')
    def test_key_order(self):
        self.assertEqual(compare(self.data),compare(dict(reversed(list(self.data.items())))))
    def test_bad_money(self):
        for bad in ['NaN','Infinity','-1','','1/2','1e3',' 49 ',49,True]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):compare(dict(self.data,baseline_price=bad))
    def test_bad_counts(self):
        for bad in [-1,1.5,True,'800',1001]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):compare(dict(self.data,retained_customers=bad))
    def test_horizon(self):
        for bad in [10,12,True,'1']:
            with self.subTest(bad=bad),self.assertRaises(ValueError):compare(dict(self.data,horizon_months=bad))
    def test_schema(self):
        d=dict(self.data);del d['unit_cost']
        with self.assertRaises(ValueError):compare(d)
        with self.assertRaises(ValueError):compare(dict(self.data,extra=1))
    def test_no_positive_margin(self):
        self.data['alternative_price']='10'
        self.assertIsNone(compare(self.data)['minimum_customers_to_exceed_baseline'])
    def test_fraction_exact(self):
        self.data.update(baseline_price='0.3',alternative_price='0.3',unit_cost='0.1',baseline_customers=3,retained_customers=3)
        self.assertEqual(compare(self.data)['baseline_contribution'],'3/5')
    def test_currency(self):
        with self.assertRaises(ValueError):compare(dict(self.data,currency='INR'))

if __name__=='__main__':unittest.main()
