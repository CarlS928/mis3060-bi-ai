# Cross-validation Prompt A: count Buy transactions by direct filtering.
# Counts rows in fact_transactions.csv where txn_type equals exactly "Buy".

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "02_Data" / "Raw" / "fact_transactions.csv"

df = pd.read_csv(DATA_PATH)

buy_count = (df["txn_type"] == "Buy").sum()

print(f"Approach A (direct filter): Buy transactions = {buy_count:,}")
