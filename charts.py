from pathlib import Path


def generate_charts(records, output_dir):
    if not records:
        print("No data available to plot.")
        return None
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib is not installed. Install it with: pip install matplotlib")
        return None

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    counts_by_date = {}
    for row in records:
        counts_by_date[row["date"]] = counts_by_date.get(row["date"], 0) + 1
    dates = sorted(counts_by_date)
    categories = {}
    for row in records:
        categories[row["category"]] = categories.get(row["category"], 0) + 1

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].plot(dates, [counts_by_date[d] for d in dates], marker="o")
    axes[0].set_title("Reports Over Time")
    axes[0].set_xlabel("Date")
    axes[0].set_ylabel("Number of reports")
    axes[0].tick_params(axis="x", rotation=45)
    axes[1].bar(list(categories.keys()), list(categories.values()))
    axes[1].set_title("Reports by Category")
    axes[1].set_ylabel("Number of reports")
    axes[1].tick_params(axis="x", rotation=65)
    fig.tight_layout()
    path = output_dir / "cleanliness_analytics.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path
