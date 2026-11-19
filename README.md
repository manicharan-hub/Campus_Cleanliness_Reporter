# Campus Cleanliness Reporter

A beginner-friendly Python 3.10+ terminal application for reporting campus cleanliness issues, tracking their status, searching records, and reviewing summary analytics.

## Features
- Menu-driven terminal interface.
- Input validation for required text, date, category, status, and severity (1–5).
- Local JSON persistence in `data/reports.json`; records remain after restart.
- View, keyword-search, and filter reports by category/status.
- Update a report's status.
- Executive summary: totals, average severity, resolution rate, status/category counts, recurring locations, and high-priority unresolved issues.
- Matplotlib chart export (reports over time and category distribution).
- CSV import with schema checks and row-by-row error reporting.
- CSV and Markdown summary export.
- Corrupted JSON is backed up before a clean file is created.

## Requirements
- Python 3.10 or newer
- Matplotlib is optional (only needed for charts)

## Run on Windows
1. Extract the ZIP file.
2. Open Command Prompt or VS Code terminal in the `Campus_Cleanliness_Reporter` folder.
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
4. Activate it:
   ```bash
   .venv\Scripts\activate
   ```
5. Install chart dependency:
   ```bash
   pip install -r requirements.txt
   ```
6. Start the application:
   ```bash
   python main.py
   ```

If you do not install Matplotlib, every other feature still works; choosing charts will show a helpful installation message.

## Demo flow for the hackathon
1. Start the app and choose `2` to show the 40 sample reports.
2. Choose `5` for the executive summary and recurring locations.
3. Choose `1` and enter severity `9` once to demonstrate validation, then enter a valid severity.
4. Choose `4` to update a report from Open to In Progress or Resolved.
5. Choose `6` to create `reports/cleanliness_analytics.png`.
6. Choose `7` to export a CSV and Markdown summary.
7. Exit and relaunch; the newly added/updated report remains saved.

## Data format
Each JSON/CSV report contains:
`id, date, location, category, severity, description, status, reported_by`

Severity is an integer from 1 (Low) to 5 (Critical). Status is Open, In Progress, or Resolved.

## Project structure
```text
Campus_Cleanliness_Reporter/
├── main.py
├── analytics.py
├── charts.py
├── requirements.txt
├── README.md
├── data/
│   ├── reports.json
│   └── sample_reports.csv
└── reports/
```

## Notes
- The application is local-first and does not require an internet connection.
- The sample data is for demonstration only. Replace it with real campus reports before operational use.
