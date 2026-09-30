"""HW3 Part 5C — cross-check 8-K extraction against yfinance (NVDA, most recent quarter)."""
import yfinance as yf

income = yf.Ticker("NVDA").quarterly_income_stmt
latest = income.columns[0]
revenue = income.loc["Total Revenue", latest]
net_income = income.loc["Net Income", latest]
print(f"NVDA quarter ending {latest.date()}")
print(f"  Total Revenue: ${revenue / 1e6:,.0f} million")
print(f"  Net Income:    ${net_income / 1e6:,.0f} million")
for label in ("Diluted EPS",):
    if label in income.index:
        print(f"  {label}:   ${income.loc[label, latest]:.2f}")
