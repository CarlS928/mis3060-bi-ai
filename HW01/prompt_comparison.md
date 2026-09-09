# Prompt Comparison — [Question chosen]

## Strategy 1 — Zero-shot

**Prompt sent:**
"What are the most important metrics for measuring credit risk in a consumer loan portfolio?"

**First 150 words of Claude's response:**
Credit risk in a consumer loan portfolio is usually assessed through a mix of borrower-level, loan-level, and portfolio-level metrics.

Borrower-level indicators start with the credit score (FICO or VantageScore) at origination and how it drifts over time, debt-to-income ratio, and payment history depth. Probability of default (PD) models translate these into a forward-looking risk estimate for each borrower or segment.

Loan-level indicators include loan-to-value ratio for secured products, the interest rate relative to risk tier, and loss given default (LGD) and exposure at default (EAD) — the three components that combine into expected loss (EL = PD × LGD × EAD).

Portfolio performance metrics are what most risk teams watch day to day: delinquency rates broken out by bucket (30, 60, 90+ days past due), net charge-off rate, roll

**Evaluation:**


---

## Strategy 2 — Role-assigned (role + audience)

**Prompt sent:**
You are a senior credit risk analyst at a large commercial bank presenting to a portfolio committee of three senior executives. The committee is reviewing the performance and risk profile of the bank’s consumer loan portfolio and wants to identify potential signs of deteriorating credit quality before they result in significant losses. The executives understand finance and banking but are not specialists in day-to-day credit risk modeling. Focus on metrics that are most useful for monitoring portfolio health, identifying emerging risk, forecasting potential losses, and supporting lending and risk-management decisions. For each metric, briefly explain what it measures, why it matters, and what an unfavorable trend could indicate.

"What are the most important metrics for measuring credit risk in a consumer loan portfolio?"

**First 150 words of Claude's response:**
A useful way to organize this for a committee is around four questions: how is the portfolio built today, how is it performing right now, where is it heading, and how much could it cost if things go wrong. Below are the metrics that map to those questions, tailored for a portfolio spanning multiple loan purposes (e.g., secured products like Auto and unsecured products like Personal loans) with varying risk profiles.

Delinquency rate by bucket (30/60/90+ days past due). Measures the share of the portfolio that has missed one or more payments, broken into severity tiers rather than one blended number. It matters because early buckets (30-day) are the leading edge of trouble — most problem loans pass through them before anything worse happens.

**Evaluation:**


---

## Strategy 3 — Few-shot

**Prompt sent:**
Use the following example to guide the structure and level of detail of your response. The example is about a different topic and is only meant to demonstrate the desired output format.
Example format:
Metric: Customer Retention Rate
What it measures: The percentage of customers who continue using a company’s services over a given period.
Why it matters: Helps evaluate customer loyalty and the stability of the company’s customer base.
What to watch for: A sustained decline could indicate increasing customer dissatisfaction or competitive pressure.
Use this framework to answer the following question: "What are the most important metrics for measuring credit risk in a consumer loan portfolio?"

**First 150 words of Claude's response:**
Metric: Order Fill Rate

What it measures: The percentage of customer orders fulfilled completely and accurately from available inventory, without stockouts or backorders.

Why it matters: Directly reflects how well supply planning matches actual demand; low fill rates signal inventory shortfalls that drive lost sales and customer attrition.

What to watch for: A declining trend alongside rising inventory levels can indicate a demand-forecasting mismatch rather than a true supply shortage.

Metric: Inventory Turnover Ratio

What it measures: How many times inventory is sold and replaced over a given period, calculated as cost of goods sold divided by average inventory.

Why it matters: Balances the cost of holding stock against the risk of stockouts

**Evaluation:**


---

## Conclusion


