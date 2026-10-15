"""Standalone synthetic monthly contribution comparison, using exact arithmetic."""
from fractions import Fraction
import json
import argparse
import re
from pathlib import Path


def money(value):
    if not isinstance(value, str) or len(value) > 32 or re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', value) is None:
        raise ValueError('Money inputs must be finite decimal strings')
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('Invalid finite money input') from exc
    if result < 0:
        raise ValueError('Money inputs cannot be negative')
    return result


def customers(value):
    if type(value) is not int or not 0 <= value <= 1_000_000_000:
        raise ValueError('Customer counts must be integers between 0 and 1000000000')
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


def load_inputs(path):
    """Reject large files and duplicate JSON keys rather than silently replacing inputs."""
    with Path(path).open('rb') as stream:
        raw = stream.read(16385)
    if len(raw) > 16384:
        raise ValueError('Input JSON must be at most 16384 bytes')
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON input field: ' + key)
            result[key] = value
        return result
    try:
        data = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_pairs)
    except (UnicodeError, RecursionError) as exc:
        raise ValueError('Input must be a shallow UTF-8 JSON object') from exc
    compare(data)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path(__file__).parent/'examples'/'pricing.json')
    args = parser.parse_args()
    try:
        result = compare(load_inputs(args.input))
    except (ValueError, OSError) as exc:
        parser.exit(2, f'Invalid scenario: {exc}\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
