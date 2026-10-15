"""Standalone synthetic monthly contribution comparison, using exact arithmetic."""
from fractions import Fraction
import json
import re
from pathlib import Path


def money(value):
    if not isinstance(value, str) or re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', value) is None:
        raise ValueError('Money inputs must be finite decimal strings')
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('Invalid finite money input') from exc
    if result < 0:
        raise ValueError('Money inputs cannot be negative')
    return result


def customers(value):
    if type(value) is not int or value < 0:
        raise ValueError('Customer counts must be nonnegative integers')
    return value


def compare(data):
    required = {'baseline_price', 'alternative_price', 'unit_cost', 'baseline_customers', 'retained_customers', 'horizon_months', 'currency'}
    if not isinstance(data, dict) or set(data) != required:
        raise ValueError('Provide exactly the documented input fields')
    if type(data['horizon_months']) is not int or data['horizon_months'] != 1:
        raise ValueError('Only a one-month comparison is supported')
    if data['currency'] != 'USD':
        raise ValueError('This example labels amounts in USD only')
    base_price, new_price, cost = (money(data[k]) for k in ('baseline_price','alternative_price','unit_cost'))
    baseline_n = customers(data['baseline_customers'])
    retained_n = customers(data['retained_customers'])
    if retained_n > baseline_n:
        raise ValueError('Retained customers cannot exceed the baseline cohort')
    base = (base_price-cost)*baseline_n
    alternative = (new_price-cost)*retained_n
    margin = new_price-cost
    threshold = None
    if margin > 0 and base >= 0:
        ratio = base/margin
        threshold = ratio.numerator//ratio.denominator + 1
    return {'baseline_contribution': str(base), 'alternative_contribution': str(alternative),
            'difference': str(alternative-base), 'comparison': 'tie' if alternative == base else ('alternative_higher' if alternative > base else 'baseline_higher'),
            'minimum_customers_to_exceed_baseline': threshold,
            'threshold_within_baseline_cohort': None if threshold is None else threshold <= baseline_n,
            'currency': 'USD', 'horizon_months': 1,
            'interpretation': 'Exact assumed contribution arithmetic; not a price recommendation or forecast'}


if __name__ == '__main__':
    print(json.dumps(compare(json.loads((Path(__file__).parent/'examples'/'pricing.json').read_text())), indent=2, sort_keys=True))
