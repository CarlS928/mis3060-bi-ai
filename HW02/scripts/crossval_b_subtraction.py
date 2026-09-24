# Cross-validation Prompt B: count Buy transactions by subtraction.
# Counts all rows in fact_transactions.csv, then subtracts the rows whose
# txn_type is Sell, Deposit, Withdrawal, Dividend, or Advisory Fee.

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "02_Data" / "Raw" / "fact_transactions.csv"
OTHER_TYPES = ["Sell", "Deposit", "Withdrawal", "Dividend", "Advisory Fee"]

df = pd.read_csv(DATA_PATH)

total_rows = len(df)
other_rows = df["txn_type"].isin(OTHER_TYPES).sum()
buy_count = total_rows - other_rows

print(f"Total rows:                         {total_rows:,}")
for txn_type in OTHER_TYPES:
    print(f"  minus {txn_type:<13}               {(df['txn_type'] == txn_type).sum():,}")
print(f"Rows of the five other types:       {other_rows:,}")
print(f"Approach B (subtraction): Buy transactions = {buy_count:,}")
