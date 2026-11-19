from datetime import date, datetime
from pathlib import Path
import csv
import json
import re
import shutil

from analytics import build_summary, print_summary
from charts import generate_charts

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
REPORTS_DIR = APP_DIR / "reports"
DATA_FILE = DATA_DIR / "reports.json"
FIELDS = ["id", "date", "location", "category", "severity", "description", "status", "reported_by"]
CATEGORIES = ["Litter", "Overflowing Dustbin", "Unclean Washroom", "Water Leakage", "Food Waste", "Blocked Drain", "Other"]
STATUSES = ["Open", "In Progress", "Resolved"]


def load_records():
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("The JSON root must be a list.")
        valid = []
        for row in data:
            if isinstance(row, dict) and all(k in row for k in FIELDS):
                valid.append(row)
        if len(valid) != len(data):
            print("WARNING: Some malformed records were skipped.")
        return valid
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        backup = DATA_FILE.with_name(f"reports_corrupt_{datetime.now():%Y%m%d_%H%M%S}.json")
        try:
            shutil.copy2(DATA_FILE, backup)
            print(f"WARNING: Invalid data backed up to {backup.name}. Starting with an empty dataset.")
        except OSError:
            print(f"WARNING: Could not back up invalid data ({exc}). Starting with an empty dataset.")
        DATA_FILE.write_text("[]", encoding="utf-8")
        return []


def save_records(records):
    DATA_DIR.mkdir(exist_ok=True)
    temp = DATA_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(DATA_FILE)


def ask_text(prompt, max_length=120):
    while True:
        value = input(prompt).strip()
        if value and len(value) <= max_length:
            return value
        print(f"Please enter 1 to {max_length} characters.")


def ask_choice(prompt, choices):
    while True:
        print(" / ".join(f"{i+1}. {item}" for i, item in enumerate(choices)))
        raw = input(prompt).strip()
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            return choices[int(raw)-1]
        for item in choices:
            if raw.casefold() == item.casefold():
                return item
        print("Invalid choice. Select a listed number or value.")


def ask_severity():
    while True:
        raw = input("Severity (1=Low to 5=Critical): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 5:
            return int(raw)
        print("Severity must be a whole number from 1 to 5.")


def ask_date():
    while True:
        raw = input(f"Report date (YYYY-MM-DD, Enter for {date.today()}): ").strip()
        if not raw:
            return date.today().isoformat()
        try:
            return date.fromisoformat(raw).isoformat()
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD (for example, 2026-11-19).")


def next_id(records):
    used = {r["id"] for r in records}
    n = 1
    while f"CLR-{n:04d}" in used:
        n += 1
    return f"CLR-{n:04d}"


def add_report(records):
    print("\n--- Submit a Cleanliness Report ---")
    location = ask_text("Location: ")
    category = ask_choice("Category: ", CATEGORIES)
    severity = ask_severity()
    description = ask_text("Describe the issue: ", 300)
    reported_by = ask_choice("Reported by: ", ["Student", "Faculty", "Housekeeping Team", "Visitor"])
    report_date = ask_date()
    record = {
        "id": next_id(records), "date": report_date, "location": location,
        "category": category, "severity": severity, "description": description,
        "status": "Open", "reported_by": reported_by
    }
    records.append(record)
    save_records(records)
    print(f"\nSUCCESS: Report {record['id']} saved locally.")
    if severity >= 4:
        print("WARNING: High-severity issue. Please notify campus maintenance promptly.")


def show_records(records):
    if not records:
        print("\nNo reports found.")
        return
    print(f"\n{'ID':<10} {'DATE':<12} {'LOCATION':<27} {'CATEGORY':<22} {'SEV':<4} {'STATUS':<12}")
    print("-" * 93)
    for r in records:
        print(f"{r['id']:<10} {r['date']:<12} {r['location'][:26]:<27} {r['category'][:21]:<22} {r['severity']:<4} {r['status']:<12}")
        print(f"    Details: {r['description']} | By: {r['reported_by']}")
    print(f"\nShowing {len(records)} report(s).")


def search_reports(records):
    print("\n--- Search Reports ---")
    term = input("Enter keyword (location, description, ID) or press Enter to skip: ").strip().casefold()
    category = input("Category filter (exact category, or Enter for all): ").strip().casefold()
    status = input("Status filter (Open / In Progress / Resolved, or Enter for all): ").strip().casefold()
    found = []
    for r in records:
        searchable = " ".join(str(r[k]) for k in ["id", "location", "description", "reported_by"]).casefold()
        if term and term not in searchable:
            continue
        if category and category != r["category"].casefold():
            continue
        if status and status != r["status"].casefold():
            continue
        found.append(r)
    show_records(found)


def update_status(records):
    report_id = input("Enter report ID: ").strip().upper()
    record = next((r for r in records if r["id"].upper() == report_id), None)
    if not record:
        print("Report ID not found.")
        return
    print(f"Current status: {record['status']}")
    record["status"] = ask_choice("Choose new status: ", STATUSES)
    save_records(records)
    print(f"Report {record['id']} updated.")


def export_reports(records):
    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = REPORTS_DIR / f"cleanliness_reports_{stamp}.csv"
    md_path = REPORTS_DIR / f"cleanliness_summary_{stamp}.md"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    summary = build_summary(records)
    lines = ["# Campus Cleanliness Reporter — Summary", "", f"- Generated: {datetime.now():%Y-%m-%d %H:%M}",
             f"- Total reports: {summary['total']}", f"- Average severity: {summary['average_severity']:.2f}/5",
             f"- Open reports: {summary['statuses'].get('Open', 0)}", "", "## Reports by status"]
    lines += [f"- {k}: {v}" for k, v in summary["statuses"].items()]
    lines += ["", "## Reports by category"] + [f"- {k}: {v}" for k, v in summary["categories"].items()]
    lines += ["", "## Most reported locations"] + [f"- {k}: {v}" for k, v in summary["locations"].most_common()]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"CSV exported: {csv_path}")
    print(f"Markdown summary exported: {md_path}")


def import_csv(records):
    path_text = input("CSV file path (default: data/sample_reports.csv): ").strip()
    path = Path(path_text) if path_text else DATA_DIR / "sample_reports.csv"
    if not path.is_absolute():
        path = APP_DIR / path
    if not path.exists():
        print("File not found.")
        return
    added = skipped = 0
    errors = []
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            required = set(FIELDS)
            if not required.issubset(set(reader.fieldnames or [])):
                print("CSV is missing required columns: " + ", ".join(sorted(required - set(reader.fieldnames or []))))
                return
            existing = {r["id"] for r in records}
            for line_no, row in enumerate(reader, start=2):
                try:
                    severity = int(row["severity"])
                    report_date = date.fromisoformat(row["date"]).isoformat()
                    if not (1 <= severity <= 5): raise ValueError("severity must be 1–5")
                    if row["category"] not in CATEGORIES: raise ValueError("unknown category")
                    if row["status"] not in STATUSES: raise ValueError("unknown status")
                    if not row["location"].strip() or not row["description"].strip(): raise ValueError("blank location/description")
                    rid = row["id"].strip() or next_id(records)
                    if rid in existing: rid = next_id(records)
                    record = {**row, "id": rid, "date": report_date, "severity": severity}
                    records.append(record); existing.add(rid); added += 1
                except (ValueError, KeyError) as exc:
                    skipped += 1; errors.append(f"Row {line_no}: {exc}")
    except (OSError, UnicodeError, csv.Error) as exc:
        print(f"Could not read CSV: {exc}")
        return
    save_records(records)
    print(f"Import complete: {added} added, {skipped} skipped.")
    for error in errors[:10]: print(" - " + error)
    if len(errors) > 10: print(f" - ...and {len(errors)-10} more error(s).")


def main():
    records = load_records()
    while True:
        print("\n" + "=" * 58)
        print("          CAMPUS CLEANLINESS REPORTER")
        print("        Cleaner Campus • Better Tomorrow")
        print("=" * 58)
        print("1. Submit a cleanliness report")
        print("2. View all reports")
        print("3. Search / filter reports")
        print("4. Update report status")
        print("5. View executive summary")
        print("6. Generate charts")
        print("7. Export CSV and Markdown summary")
        print("8. Import reports from CSV")
        print("9. Exit")
        choice = input("\nChoose an option (1-9): ").strip()
        if choice == "1": add_report(records)
        elif choice == "2": show_records(records)
        elif choice == "3": search_reports(records)
        elif choice == "4": update_status(records)
        elif choice == "5": print_summary(build_summary(records))
        elif choice == "6":
            result = generate_charts(records, REPORTS_DIR)
            if result: print("Charts saved in:", result)
        elif choice == "7": export_reports(records)
        elif choice == "8": import_csv(records)
        elif choice == "9":
            save_records(records)
            print("Thank you for helping keep the campus clean. Goodbye!")
            break
        else: print("Invalid menu option. Enter a number from 1 to 9.")


if __name__ == "__main__":
    main()
