from collections import Counter
from statistics import mean


def build_summary(records):
    statuses = Counter(r["status"] for r in records)
    categories = Counter(r["category"] for r in records)
    locations = Counter(r["location"] for r in records)
    severities = [int(r["severity"]) for r in records]
    return {
        "total": len(records),
        "average_severity": mean(severities) if severities else 0.0,
        "statuses": statuses,
        "categories": categories,
        "locations": locations,
        "high_priority_open": sum(1 for r in records if int(r["severity"]) >= 4 and r["status"] != "Resolved")
    }


def print_summary(summary):
    print("\n" + "=" * 48)
    print("             EXECUTIVE SUMMARY")
    print("=" * 48)
    print(f"Total reports          : {summary['total']}")
    print(f"Average severity       : {summary['average_severity']:.2f} / 5")
    print(f"High-priority unresolved: {summary['high_priority_open']}")
    print("\nReports by status:")
    for key in ["Open", "In Progress", "Resolved"]:
        print(f"  {key:<18}: {summary['statuses'].get(key, 0)}")
    print("\nReports by category:")
    for key, value in summary["categories"].most_common():
        print(f"  {key:<22}: {value}")
    print("\nMost reported locations:")
    if summary["locations"]:
        for key, value in summary["locations"].most_common(5):
            print(f"  {key:<30}: {value}")
    else:
        print("  No location data yet.")
    if summary["total"]:
        resolved = summary["statuses"].get("Resolved", 0)
        print(f"\nResolution rate        : {resolved / summary['total'] * 100:.1f}%")
