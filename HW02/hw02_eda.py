# =============================================================================
# Script:    hw02_eda.py
# Purpose:   Exploratory data analysis (EDA) of Wildcat Capital's client
#            transaction history. Prints a data profile to the terminal, saves
#            three charts, and writes a plain-text summary file.
# Dataset:   fact_transactions.csv -- every client transaction recorded in
#            Wildcat Capital's portfolio management system, Jan 2020 - Dec 2024
#            (Buy, Sell, Deposit, Withdrawal, Dividend, Advisory Fee).
# Author:    Carl Söderman
# Course:    MIS3060 Business Intelligence with AI -- HW02
# Generated: 2026-09-23 (from specification.md)
#
# Inputs:    HW02/02_Data/Raw/fact_transactions.csv   (read-only)
# Outputs:   HW02/charts/hist_amount.png
#            HW02/charts/box_amount_by_type.png
#            HW02/charts/scatter_shares_amount.png
#            HW02/hw02_profile.txt
#
# Run from the VS Code terminal with the virtual environment active:
#     python hw02_eda.py
# =============================================================================

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # save charts to file without opening windows
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# --- File locations (relative to this script, so it runs from any folder) ---
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "02_Data" / "Raw" / "fact_transactions.csv"
CHART_DIR = BASE_DIR / "charts"
PROFILE_PATH = BASE_DIR / "hw02_profile.txt"

EXPECTED_SHAPE = (298772, 9)

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)

# Everything printed through report() is also collected for hw02_profile.txt
summary_lines = []


def report(text=""):
    """Print text to the terminal and keep a copy for the summary file."""
    print(text)
    summary_lines.append(str(text))


def section(title):
    """Print a section heading."""
    report()
    report(f"=== {title} ===")


def money(value):
    """Format a number as dollars with commas and two decimals."""
    return f"${value:,.2f}"


# --- Step 2: Load the data (txn_date is left as stored, i.e. text) ----------
df = pd.read_csv(DATA_PATH)

report("WILDCAT CAPITAL -- fact_transactions.csv DATA PROFILE")
report(f"Source file: {DATA_PATH}")

# --- Step 3: Shape -----------------------------------------------------------
section("3. Shape")
rows, cols = df.shape
report(f"Rows:    {rows:,}")
report(f"Columns: {cols}")

# --- Step 4: Column names and data types -------------------------------------
section("4. Column Names and Data Types")
dtypes_table = pd.DataFrame({"column": df.columns, "dtype": df.dtypes.astype(str).values})
report(dtypes_table.to_string(index=False))

# --- Step 5: Missing values --------------------------------------------------
section("5. Missing Values")
missing = pd.DataFrame({
    "missing": df.isna().sum(),
    "pct_of_rows": (df.isna().mean() * 100).round(2),
})
report(missing.to_string())

# --- Step 6: Descriptive statistics for numeric columns ----------------------
section("6. Descriptive Statistics (numeric columns)")
desc = df.describe().T
desc = desc.rename(columns={"50%": "median", "25%": "25th pct", "75%": "75th pct"})
desc = desc[["count", "mean", "std", "min", "25th pct", "median", "75th pct", "max"]]
report(desc.round(2).to_string())

# --- Step 7: Transaction type breakdown --------------------------------------
section("7. Transaction Type Breakdown")
type_counts = df["txn_type"].value_counts()
type_table = pd.DataFrame({
    "count": type_counts,
    "percent": (type_counts / len(df) * 100).round(2),
})
report(type_table.to_string())

# --- Step 8: Unique clients, advisors, and securities ------------------------
section("8. Unique Entities")
report(f"Unique clients (client_id):      {df['client_id'].nunique():,}")
report(f"Unique advisors (advisor_id):    {df['advisor_id'].nunique():,}")
report(f"Unique securities (security_id): {df['security_id'].nunique():,}")

# --- Step 9: Date range ------------------------------------------------------
section("9. Date Range")
report(f"Earliest txn_date: {df['txn_date'].min()}")
report(f"Latest txn_date:   {df['txn_date'].max()}")

# --- Step 10: Duplicate txn_id check -----------------------------------------
section("10. Duplicate Check (txn_id)")
dup_count = df["txn_id"].duplicated().sum()
report(f"Duplicate txn_id values: {dup_count:,}")

# --- Step 11: Amount distribution --------------------------------------------
section("11. Amount Distribution")
amount_mean = df["amount"].mean()
amount_median = df["amount"].median()
amount_skew = df["amount"].skew()
if amount_skew > 0.5:
    skew_label = "right-skewed"
elif amount_skew < -0.5:
    skew_label = "left-skewed"
else:
    skew_label = "approximately symmetric"
report(f"Mean amount:   {money(amount_mean)}")
report(f"Median amount: {money(amount_median)}")
report(f"Skewness:      {amount_skew:.2f} ({skew_label})")

# --- Step 12: Amount by transaction type -------------------------------------
section("12. Amount by Transaction Type (sorted by mean, highest first)")
by_type = (
    df.groupby("txn_type")["amount"]
    .agg(count="count", mean_amount="mean", median_amount="median")
    .sort_values("mean_amount", ascending=False)
)
by_type_display = by_type.copy()
by_type_display["count"] = by_type_display["count"].map("{:,}".format)
by_type_display["mean_amount"] = by_type_display["mean_amount"].map(money)
by_type_display["median_amount"] = by_type_display["median_amount"].map(money)
report(by_type_display.to_string())

# --- Step 13: Correlations ---------------------------------------------------
section("13. Correlation Matrix (shares, price, amount)")
corr_cols = ["shares", "price", "amount"]
corr = df[corr_cols].corr().round(2)
report(corr.to_string())

# Each pair once, excluding a variable with itself; rank by strength (|r|)
pairs = []
for i, a in enumerate(corr_cols):
    for b in corr_cols[i + 1:]:
        pairs.append((a, b, corr.loc[a, b]))
pairs.sort(key=lambda p: abs(p[2]), reverse=True)
report()
report("Strongest correlations (by absolute value):")
for rank, (a, b, r) in enumerate(pairs[:3], start=1):
    report(f"  {rank}. {a} - {b}: {r:.2f}")

# --- Step 14: Negative shares by transaction type ----------------------------
section("14. Shares by Transaction Type (min, max, negative count)")
shares_by_type = df.groupby("txn_type")["shares"].agg(
    min_shares="min",
    max_shares="max",
    negative_count=lambda s: int((s < 0).sum()),
)
report(shares_by_type.round(4).fillna("n/a").to_string())
report(f"Total rows with negative shares: {int((df['shares'] < 0).sum()):,}")

# --- Step 15: Shape check ----------------------------------------------------
section("15. Shape Check")
if df.shape != EXPECTED_SHAPE:
    report("*" * 60)
    report("WARNING: dataset shape does not match the expected shape!")
    report(f"  Expected: {EXPECTED_SHAPE[0]:,} rows x {EXPECTED_SHAPE[1]} columns")
    report(f"  Actual:   {df.shape[0]:,} rows x {df.shape[1]} columns")
    report("*" * 60)
else:
    report(f"OK: shape matches the expected {EXPECTED_SHAPE[0]:,} rows x {EXPECTED_SHAPE[1]} columns.")

# --- Step 16: Charts ---------------------------------------------------------
CHART_DIR.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid")

# Histogram of amount with mean and median lines
hist_path = CHART_DIR / "hist_amount.png"
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df["amount"], bins=100, color="steelblue", edgecolor="white", linewidth=0.3)
ax.axvline(amount_mean, color="firebrick", linestyle="--", linewidth=2,
           label=f"Mean: {money(amount_mean)}")
ax.axvline(amount_median, color="darkorange", linestyle="-", linewidth=2,
           label=f"Median: {money(amount_median)}")
ax.set_title("Distribution of Transaction Amount")
ax.set_xlabel("Amount ($)")
ax.set_ylabel("Number of transactions")
ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("${x:,.0f}"))
ax.legend()
fig.tight_layout()
fig.savefig(hist_path, dpi=150)
plt.close(fig)

# Horizontal box plot of amount by transaction type
box_path = CHART_DIR / "box_amount_by_type.png"
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x="amount", y="txn_type", order=by_type.index, orient="h",
            color="lightsteelblue", fliersize=1, ax=ax)
ax.set_title("Transaction Amount by Transaction Type")
ax.set_xlabel("Amount ($)")
ax.set_ylabel("Transaction type")
ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("${x:,.0f}"))
fig.tight_layout()
fig.savefig(box_path, dpi=150)
plt.close(fig)

# Scatter of shares vs amount, colored by transaction type
scatter_path = CHART_DIR / "scatter_shares_amount.png"
fig, ax = plt.subplots(figsize=(10, 6))
scatter_data = df.dropna(subset=["shares"])
palette = sns.color_palette("tab10", n_colors=df["txn_type"].nunique())
for color, (txn_type, group) in zip(palette, scatter_data.groupby("txn_type")):
    ax.scatter(group["shares"], group["amount"], s=3, alpha=0.3, color=color,
               label=txn_type, rasterized=True)
ax.set_title("Shares vs. Transaction Amount by Transaction Type")
ax.set_xlabel("Shares")
ax.set_ylabel("Amount ($)")
ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("${x:,.0f}"))
ax.legend(title="Transaction type", markerscale=4)
fig.tight_layout()
fig.savefig(scatter_path, dpi=150)
plt.close(fig)

# --- Step 17: Save the plain-text summary ------------------------------------
PROFILE_PATH.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

print()
print("=== Done ===")
print("Script finished successfully. Files saved:")
for path in (hist_path, box_path, scatter_path, PROFILE_PATH):
    print(f"  {path}")
