"""
Generate dashboard metrics for zero-sim compliance progress.

This script tracks weekly progress toward zero violations and provides
trend analysis for stakeholder visibility.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


def parse_report(report_path: Path) -> Dict[str, Any]:
    """Load and parse a violation report"""
    with open(report_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_dashboard(reports_dir: str = "reports/zero_sim"):
    """Generate weekly dashboard from violation reports"""
    reports_path = Path(reports_dir)

    if not reports_path.exists():
        print(f"⚠️  Reports directory not found: {reports_dir}")
        print("   Run zero_sim_analyzer.py first to generate reports.")
        return

    reports = sorted(reports_path.glob("violation_report_*.json"), reverse=True)

    if not reports:
        print(f"⚠️  No reports found in {reports_dir}")
        print(
            "   Run zero_sim_analyzer.py --output reports/zero_sim/violation_report_YYYY-MM-DD.json"
        )
        return

    # Load latest 4 weeks
    week_data = []
    for report_file in reports[:4]:
        try:
            data = parse_report(report_file)
            week_data.append(
                {
                    "date": report_file.stem.split("_")[-1],
                    "total": data["total_violations"],
                    "auto_fixable": data["auto_fixable"],
                    "manual_review": data["manual_review"],
                    "by_severity": data.get("by_severity", {}),
                }
            )
        except Exception as e:
            print(f"⚠️  Error parsing {report_file}: {e}")

    if not week_data:
        print("⚠️  No valid reports found")
        return

    # Reverse to ascending order
    week_data = week_data[::-1]

    print("=" * 80)
    print("ZERO-SIM COMPLIANCE DASHBOARD (4-Week Trend)")
    print("=" * 80)
    print(f"{'Week':<15} {'Total':<12} {'Auto-Fix':<12} {'Manual':<12} {'Change':<15}")
    print("-" * 80)

    for i, week in enumerate(week_data):
        change = ""
        if i > 0:
            diff = week_data[i - 1]["total"] - week["total"]
            if diff > 0:
                change = f"↓ {diff} ({-diff / week_data[i - 1]['total'] * 100:.1f}%)"
            elif diff < 0:
                change = f"↑ {-diff} ({diff / week_data[i - 1]['total'] * 100:.1f}%)"
            else:
                change = "→ 0"

        print(
            f"{week['date']:<15} {week['total']:<12} {week['auto_fixable']:<12} "
            f"{week['manual_review']:<12} {change:<15}"
        )

    # Projection
    print("-" * 80)
    if len(week_data) >= 2:
        trend = week_data[-1]["total"] - week_data[0]["total"]
        avg_reduction = trend / len(week_data)
        weeks_to_zero = (
            abs(week_data[-1]["total"] / avg_reduction)
            if avg_reduction < 0
            else float("inf")
        )

        print(f"Average trend: {avg_reduction:.1f} violations/week")
        if avg_reduction < 0:
            print(
                f"Projected completion: {weeks_to_zero:.1f} weeks ({datetime.now() + timedelta(weeks=weeks_to_zero):%Y-%m-%d})"
            )
        elif avg_reduction > 0:
            print("⚠️  Trend reversed: violations increasing")
        else:
            print("→ Trend flat: no change")

    # Severity breakdown for latest week
    if week_data:
        latest = week_data[-1]
        print("\nLatest Week Severity Breakdown:")
        for severity, count in latest.get("by_severity", {}).items():
            pct = count / latest["total"] * 100 if latest["total"] > 0 else 0
            print(f"  {severity}: {count} ({pct:.1f}%)")

    print("=" * 80)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Zero-Sim Compliance Dashboard")
    parser.add_argument(
        "--reports-dir",
        default="reports/zero_sim",
        help="Directory containing violation reports",
    )
    args = parser.parse_args()

    generate_dashboard(args.reports_dir)


if __name__ == "__main__":
    main()
