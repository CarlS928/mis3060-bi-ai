"""
HW3 Part 4 — Corporate Events Timeline

Joins executive_events.csv to earnings_history.csv: for each executive event,
finds the nearest earnings (Item 2.02) filing for the same company, measures
the gap in days, and labels the event 'before earnings', 'after earnings' or
'same week' (within 7 days of an earnings filing).

Output: hw03/corporate_events_timeline.csv
Run:    python hw03/hw03_timeline.py
"""

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
EARNINGS_CSV = HERE / "earnings_history.csv"
EVENTS_CSV = HERE / "executive_events.csv"
OUT_CSV = HERE / "corporate_events_timeline.csv"
SAME_WEEK_DAYS = 7


def nearest_earnings(event, earnings):
    """Return the earnings row whose filing_date is closest to the event's filing_date."""
    same_company = earnings[earnings["ticker"] == event["ticker"]]
    if same_company.empty:
        return None
    gaps = (event["filing_date"] - same_company["filing_date"]).abs()
    return same_company.loc[gaps.idxmin()]


def classify(signed_days):
    """signed_days = event date minus earnings date (negative = event came first)."""
    if abs(signed_days) <= SAME_WEEK_DAYS:
        return "same week"
    return "before earnings" if signed_days < 0 else "after earnings"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    earnings = pd.read_csv(EARNINGS_CSV, dtype={"cik": str}, parse_dates=["filing_date"])
    events = pd.read_csv(EVENTS_CSV, dtype={"cik": str}, parse_dates=["filing_date"])

    # earnings columns are prefixed so both source tables' columns survive the join
    earnings_cols = {c: f"earnings_{c}" for c in earnings.columns
                     if c not in ("company", "ticker", "cik")}

    rows = []
    for _, event in events.iterrows():
        row = event.to_dict()
        match = nearest_earnings(event, earnings)
        if match is None:
            for new in earnings_cols.values():
                row[new] = None
            row["days_to_nearest_earnings"] = None
            row["event_timing"] = "no earnings data"
        else:
            for old, new in earnings_cols.items():
                row[new] = match[old]
            signed = (event["filing_date"] - match["filing_date"]).days
            row["days_to_nearest_earnings"] = abs(signed)
            row["signed_days"] = signed
            row["event_timing"] = classify(signed)
        rows.append(row)

    timeline = pd.DataFrame(rows)
    for col in ("filing_date", "earnings_filing_date"):
        if col in timeline:
            timeline[col] = pd.to_datetime(timeline[col]).dt.strftime("%Y-%m-%d")
    ordered = (list(events.columns) + list(earnings_cols.values())
               + ["days_to_nearest_earnings", "signed_days", "event_timing"])
    timeline = timeline.reindex(columns=ordered).sort_values(["ticker", "filing_date"])
    timeline.to_csv(OUT_CSV, index=False)

    # -- Summary by company --------------------------------------------------
    print("=" * 78)
    print("CORPORATE EVENTS TIMELINE — executive changes vs. nearest earnings filing")
    print("=" * 78)
    for ticker in earnings["ticker"].unique():
        company_rows = timeline[timeline["ticker"] == ticker]
        print(f"\n{ticker}")
        if company_rows.empty:
            print("  No executive events in past 12 months")
            continue
        for _, r in company_rows.iterrows():
            who = ("(compensation-only 5.02 filing, no personnel change)"
                   if r["event_type"] == "other"
                   else f"{r['event_type']}: {r['person_name']} — {r['title']}")
            direction = "before" if r["signed_days"] < 0 else "after"
            print(f"  {r['filing_date']}  {who}")
            print(f"      {r['event_timing']:<16} {r['days_to_nearest_earnings']:>3} days "
                  f"{direction} earnings filed {r['earnings_filing_date']} ({r['earnings_period']})")

    # -- Final counts ---------------------------------------------------------
    people = timeline[timeline["event_type"] != "other"]
    counts = people["event_timing"].value_counts()
    print("\n" + "=" * 78)
    print(f"FINAL COUNT — {len(people)} personnel events across all five companies "
          f"({len(timeline) - len(people)} compensation-only 'other' rows excluded)")
    for label in ("before earnings", "after earnings", "same week"):
        print(f"  {label:<16} {counts.get(label, 0)}")
    print(f"\nSaved {len(timeline)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
