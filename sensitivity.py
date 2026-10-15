"""Enumerate stated retention assumptions; no statistical probability model."""
import argparse
import json
from pathlib import Path
from pricing import compare


def sensitivity(data, retained_counts):
    """Compare up to 101 distinct scenarios in deterministic count order."""
    compare(data)  # Validate the baseline even when no scenario is requested.
    if not isinstance(retained_counts, list) or not 1 <= len(retained_counts) <= 101:
        raise ValueError('Provide between 1 and 101 retained-customer scenarios')
    if any(type(n) is not int for n in retained_counts):
        raise ValueError('Scenario counts must be integers')
    if len(set(retained_counts)) != len(retained_counts):
        raise ValueError('Scenario counts must be unique')
    rows = [dict(retained_customers=n, **compare(dict(data, retained_customers=n)))
            for n in sorted(retained_counts)]
    return {'scenario_count': len(rows), 'rows': rows,
            'interpretation': 'Enumerated assumptions only; no probabilities or predicted retention'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path(__file__).parent/'examples'/'pricing.json')
    parser.add_argument('--retained', type=int, nargs='+', default=[600, 661, 662, 800, 1000])
    args = parser.parse_args()
    try:
        from pricing import load_inputs
        result = sensitivity(load_inputs(args.input), args.retained)
    except (ValueError, OSError) as exc:
        parser.exit(2, f'Invalid scenario: {exc}\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
