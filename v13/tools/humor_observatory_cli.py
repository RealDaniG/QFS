"""
CLI tool for humor signal observability

This tool provides a command-line interface for operators to inspect
humor signal statistics, distributions, and anomalies.
"""
from fractions import Fraction
from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import json
import argparse
from typing import Dict, Any, List
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from v13.policy.humor_policy import HumorSignalPolicy
from v13.policy.humor_observatory import HumorSignalObservatory, HumorSignalSnapshot

class HumorObservatoryCLI:
    """CLI interface for humor signal observability."""

    def __init__(self):
        """Initialize the CLI tool."""
        self.humor_policy = HumorSignalPolicy()
        self.observatory = HumorSignalObservatory()

    def load_sample_data(self):
        """Load sample data for demonstration."""
        sample_snapshots = [HumorSignalSnapshot(timestamp=1000 + i * 100, content_id=f'sample_content_{i}', dimensions={'chronos': Fraction(1, 2) + i % 3 * Fraction(1, 5), 'lexicon': Fraction(2, 5) + i % 4 * Fraction(3, 20), 'surreal': Fraction(3, 10) + i % 5 * Fraction(1, 10), 'empathy': Fraction(3, 5) + i % 2 * Fraction(1, 5), 'critique': Fraction(1, 2) + i % 3 * Fraction(3, 20), 'slapstick': Fraction(1, 5) + i % 4 * Fraction(1, 5), 'meta': Fraction(2, 5) + i % 6 * Fraction(1, 10)}, confidence=Fraction(7, 10) + i % 4 * Fraction(1, 20), bonus_factor=Fraction(1, 10) + i % 5 * Fraction(3, 100), policy_version='v1.0.0') for i in range(20)]
        for snapshot in sorted(sample_snapshots):
            self.observatory.record_signal(snapshot)
        print(f'Loaded {len(sample_snapshots)} sample humor signal snapshots')

    def show_summary(self):
        """Show summary statistics."""
        report = self.observatory.get_observability_report()
        print('\n=== HUMOR SIGNAL OBSERVABILITY SUMMARY ===')
        print(f'Total signals processed: {report.total_signals_processed}')
        print(f'Average confidence: {report.average_confidence:.3f}')
        print(f'Anomalies detected: {report.anomaly_count}')
        print('\nDimension Averages:')
        for dimension, avg in report.dimension_averages.items():
            print(f'  {dimension:12}: {avg:.3f}')
        print('\nBonus Statistics:')
        print(f"  Mean bonus  : {report.bonus_statistics.get('mean', 0):.3f}")
        print(f"  Min bonus   : {report.bonus_statistics.get('min', 0):.3f}")
        print(f"  Max bonus   : {report.bonus_statistics.get('max', 0):.3f}")
        print(f"  Std dev     : {report.bonus_statistics.get('std_dev', 0):.3f}")

    def show_distributions(self):
        """Show dimension distributions."""
        report = self.observatory.get_observability_report()
        print('\n=== DIMENSION DISTRIBUTIONS ===')
        for dimension, distribution in report.dimension_distributions.items():
            print(f'\n{dimension.upper()}:')
            sorted_buckets = sorted(distribution.items(), key=lambda x: qnum(x[0].split('-')[0]))
            for bucket, percentage in sorted(sorted_buckets):
                bar_length = int(percentage * 50)
                bar = '█' * bar_length
                print(f'  {bucket:8}: {bar} ({percentage:.1%})')

    def show_top_content(self):
        """Show top performing content."""
        report = self.observatory.get_observability_report()
        print('\n=== TOP PERFORMING CONTENT ===')
        if not report.top_performing_content:
            print('No content data available')
            return
        print(f"{'Rank':<4} {'Content ID':<15} {'Bonus':<8} {'Confidence':<10} {'Top Dimension'}")
        print('-' * 60)
        for i, content in enumerate(report.top_performing_content, 1):
            top_dim = max(content['dimensions'].items(), key=lambda x: x[1])
            print(f"{i:<4} {content['content_id']:<15} {content['bonus_factor']:<8.3f} {content['confidence']:<10.3f} {top_dim[0]} ({top_dim[1]:.2f})")

    def show_correlations(self):
        """Show dimension correlations."""
        correlations = self.observatory.get_dimension_correlations()
        if not correlations:
            print('\nNo correlation data available')
            return
        print('\n=== DIMENSION CORRELATIONS ===')
        dimensions = sorted(correlations.keys())
        print(f"{'':<12}", end='')
        for dim in sorted(dimensions):
            print(f'{dim:<8}', end='')
        print()
        for dim1 in sorted(dimensions):
            print(f'{dim1:<12}', end='')
            for dim2 in sorted(dimensions):
                corr = correlations[dim1][dim2]
                if dim1 == dim2:
                    print(f"{'1.000':<8}", end='')
                else:
                    print(f'{corr:<8.3f}', end='')
            print()

    def export_data(self, filepath: str):
        """Export observability data to JSON file."""
        export_data = self.observatory.export_observability_data()
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f'\nData exported to {filepath}')

    def run(self, args):
        """Run the CLI tool with given arguments."""
        if args.load_sample:
            self.load_sample_data()
        if args.summary:
            self.show_summary()
        if args.distributions:
            self.show_distributions()
        if args.top_content:
            self.show_top_content()
        if args.correlations:
            self.show_correlations()
        if args.export:
            self.export_data(args.export)

def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(description='Humor Signal Observatory CLI')
    parser.add_argument('--load-sample', action='store_true', help='Load sample data for demonstration')
    parser.add_argument('--summary', action='store_true', help='Show summary statistics')
    parser.add_argument('--distributions', action='store_true', help='Show dimension distributions')
    parser.add_argument('--top-content', action='store_true', help='Show top performing content')
    parser.add_argument('--correlations', action='store_true', help='Show dimension correlations')
    parser.add_argument('--export', metavar='FILEPATH', help='Export data to JSON file')
    if len(sys.argv) == 1:
        sys.argv.append('--summary')
    args = parser.parse_args()
    cli = HumorObservatoryCLI()
    cli.run(args)
if __name__ == '__main__':
    main()